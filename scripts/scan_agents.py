#!/usr/bin/env python3
"""
Agent Contract System — Project Scanner
Scans any project for AI agents, shared resources, and collision zones.

Works with:
- Claude Code projects (CLAUDE.md files, .claude/ directories)
- OpenClaw workspaces (skills/, cron jobs, agents/)
- Any project with multiple agents touching shared files
"""

import os
import sys
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def scan_project(project_root: Path) -> dict:
    """Main scanner — returns full project inventory."""
    
    results = {
        "project": str(project_root),
        "scan_date": datetime.now().isoformat(),
        "agents": [],
        "shared_resources": [],
        "collision_zones": [],
        "unowned_resources": [],
    }
    
    # Phase 1: Discover agents
    results["agents"] = discover_agents(project_root)
    
    # Phase 2: Discover shared resources (files touched by agents)
    resources = discover_shared_resources(project_root, results["agents"])
    results["shared_resources"] = resources
    
    # Phase 3: Find collision zones (resources touched by multiple agents)
    results["collision_zones"] = find_collisions(resources)
    
    # Phase 4: Flag unowned resources
    results["unowned_resources"] = [
        r for r in resources 
        if r.get("touched_by", []) and not r.get("owner")
    ]
    
    return results


def discover_agents(project_root: Path) -> list:
    """Discover AI agents in the project.
    
    Detection strategies:
    1. Claude Code: CLAUDE.md files, .claude/agents/ directories
    2. OpenClaw: skills/*/SKILL.md, cron job references in MEMORY.md
    3. General: Any agent config files, system prompt files
    """
    agents = []
    agent_id = 0
    
    # ── Claude Code: CLAUDE.md files ──
    for claude_md in project_root.rglob("CLAUDE.md"):
        # Skip node_modules, .git, etc.
        if any(skip in str(claude_md) for skip in ["node_modules", ".git", "__pycache__", "venv"]):
            continue
        try:
            content = claude_md.read_text()
            agent_id += 1
            agents.append({
                "id": f"AGT-{agent_id:03d}",
                "name": claude_md.parent.name if claude_md.parent != project_root else "main",
                "type": "claude-code",
                "path": str(claude_md),
                "role": extract_role(content),
                "reads": extract_file_refs(content, claude_md.parent),
                "writes": extract_write_refs(content, claude_md.parent),
                "system_prompt_preview": content[:500] if len(content) > 500 else content,
            })
        except Exception:
            pass
    
    # ── Claude Code: .claude/agents/ directories ──
    claude_agents_dir = project_root / ".claude" / "agents"
    if claude_agents_dir.exists():
        for agent_dir in claude_agents_dir.iterdir():
            if agent_dir.is_dir():
                agent_md = agent_dir / "CLAUDE.md" or agent_dir / "system.md"
                # Check for any markdown file
                md_files = list(agent_dir.glob("*.md"))
                prompt_file = md_files[0] if md_files else None
                if prompt_file:
                    try:
                        content = prompt_file.read_text()
                        agent_id += 1
                        agents.append({
                            "id": f"AGT-{agent_id:03d}",
                            "name": agent_dir.name,
                            "type": "claude-code-agent",
                            "path": str(prompt_file),
                            "role": extract_role(content),
                            "reads": extract_file_refs(content, agent_dir),
                            "writes": extract_write_refs(content, agent_dir),
                        })
                    except Exception:
                        pass
    
    # ── OpenClaw: skills ──
    skills_dir = project_root / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    try:
                        content = skill_md.read_text()
                        agent_id += 1
                        agents.append({
                            "id": f"AGT-{agent_id:03d}",
                            "name": skill_dir.name,
                            "type": "openclaw-skill",
                            "path": str(skill_md),
                            "role": extract_first_heading(content) or "Skill",
                            "reads": extract_file_refs(content, skill_dir),
                            "writes": extract_write_refs(content, skill_dir),
                        })
                    except Exception:
                        pass
    
    # ── General: any file that looks like an agent definition ──
    agent_indicators = ["system prompt", "you are an ai", "you are a", "agent role:"]
    agent_pattern_files = project_root.glob("agents/**/*.md") if (project_root / "agents").exists() else []
    for agent_file in agent_pattern_files:
        try:
            content = agent_file.read_text().lower()
            if any(indicator in content for indicator in agent_indicators):
                agent_id += 1
                agents.append({
                    "id": f"AGT-{agent_id:03d}",
                    "name": agent_file.stem,
                    "type": "general-agent",
                    "path": str(agent_file),
                    "role": extract_role(agent_file.read_text()),
                    "reads": [],
                    "writes": [],
                })
        except Exception:
            pass
    
    return agents


def discover_shared_resources(project_root: Path, agents: list) -> list:
    """Discover resources shared between agents.
    
    Looks for:
    - Files referenced by multiple agents
    - Database tables mentioned in prompts
    - API endpoints referenced
    - Templates, configs, data files
    """
    resources = []
    file_touch_map = defaultdict(list)  # path -> [agent_ids]
    db_touch_map = defaultdict(list)
    api_touch_map = defaultdict(list)
    
    # Collect all file references from agents
    for agent in agents:
        for ref in agent.get("reads", []):
            resolved = resolve_path(ref, project_root, Path(agent["path"]).parent)
            if resolved:
                file_touch_map[resolved].append(agent["id"])
        for ref in agent.get("writes", []):
            resolved = resolve_path(ref, project_root, Path(agent["path"]).parent)
            if resolved:
                file_touch_map[resolved].append(agent["id"])
    
    # Also scan for commonly shared file types
    shared_patterns = [
        "**/*.template.*", "**/*.config.*", "**/config.*",
        "**/.env*", "**/schema.*", "**/*.sql",
        "**/templates/**", "**/data/**/*.csv", "**/data/**/*.json",
        "**/*.yml", "**/*.yaml", "**/Makefile", "**/docker-compose*",
        "**/package.json", "**/requirements*.txt", "**/pyproject.toml",
    ]
    
    for pattern in shared_patterns:
        for matched in project_root.glob(pattern):
            path_str = str(matched.relative_to(project_root))
            if any(skip in path_str for skip in ["node_modules", ".git", "__pycache__", "venv", ".venv"]):
                continue
            # Check if any agent references this file
            for agent in agents:
                agent_dir = Path(agent["path"]).parent
                for ref in agent.get("reads", []) + agent.get("writes", []):
                    resolved = resolve_path(ref, project_root, agent_dir)
                    if resolved and resolved == path_str:
                        file_touch_map[path_str].append(agent["id"])
                        break
                else:
                    # Even if no explicit reference, flag if it's a known shared type
                    if any(ext in matched.suffix for ext in [".json", ".yaml", ".yml", ".env", ".sql"]):
                        file_touch_map[path_str].append(agent["id"])
                        break
    
    # Build resource entries
    for path, agent_ids in file_touch_map.items():
        unique_agents = list(set(agent_ids))
        resource = {
            "type": "file",
            "path": path,
            "touched_by": unique_agents,
            "collision": len(unique_agents) > 1,
            "owner": None,  # To be filled by human
            "readers": unique_agents,
        }
        resources.append(resource)
    
    return resources


def find_collisions(resources: list) -> list:
    """Identify collision zones — resources touched by multiple agents with no owner."""
    collisions = []
    for r in resources:
        if r.get("collision") and len(r.get("touched_by", [])) > 1:
            # Check if agents are writing (not just reading)
            collisions.append({
                "resource": r["path"],
                "type": r["type"],
                "agents": r["touched_by"],
                "risk": "HIGH" if r.get("writes", False) else "MEDIUM",
                "resolution": "Assign an owner. Define who writes, who reads.",
            })
    return collisions


def extract_role(content: str) -> str:
    """Extract agent role from prompt content."""
    patterns = [
        r'(?:you are|role:|you are an?|acting as)\s*(?:an?\s*)?["\']?([A-Za-z0-9 /&-]+?)(?:["\']?\s*(?:agent|assistant|specialist|expert|bot))',
        r'(?:role|purpose|job)[\s:]+["\']?([A-Za-z0-9 /&-]+)["\']?',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Fallback: first heading
    heading = extract_first_heading(content)
    return heading or "Unknown role"


def extract_file_refs(content: str, base_dir: Path) -> list:
    """Extract file references from agent content."""
    refs = []
    patterns = [
        r'(?:read|open|load|check|consult|see)\s+(?:the\s+)?(?:file\s+)?["\']?([\w./_-]+\.[\w]+)["\']?',
        r'(?:from|in)\s+(?:the\s+)?(?:file\s+)?["\']?([\w./_-]+\.[\w]+)["\']?',
        r'`([\w./_-]+\.[\w]+)`',
        r'(?:AGENT_CONTRACT|README|CONFIG|SCHEMA|\.env[.\w]*)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        refs.extend(matches)
    return list(set(refs))


def extract_write_refs(content: str, base_dir: Path) -> list:
    """Extract file write references from agent content."""
    refs = []
    patterns = [
        r'(?:write|save|create|update|modify|edit|overwrite|output to)\s+(?:the\s+)?(?:file\s+)?["\']?([\w./_-]+\.[\w]+)["\']?',
        r'(?:export|dump|persist|store)\s+(?:to\s+)?["\']?([\w./_-]+\.[\w]+)["\']?',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        refs.extend(matches)
    return list(set(refs))


def resolve_path(ref: str, project_root: Path, agent_dir: Path) -> str | None:
    """Resolve a file reference to a relative path from project root. Returns None if unresolvable."""
    # Skip if it's not a file reference
    if not re.search(r'\.[a-zA-Z]{1,6}$', ref) and not any(
        kw in ref.upper() for kw in ["CONFIG", "SCHEMA", "README", "CONTRACT", "MAKEFILE"]
    ):
        return None
    
    ref_path = Path(ref)
    if ref_path.is_absolute():
        try:
            return str(ref_path.relative_to(project_root))
        except ValueError:
            return None
    
    # Try relative to agent directory
    candidate = (agent_dir / ref_path).resolve()
    try:
        return str(candidate.relative_to(project_root))
    except ValueError:
        pass
    
    # Try relative to project root
    candidate = (project_root / ref_path).resolve()
    try:
        return str(candidate.relative_to(project_root))
    except ValueError:
        return None
    
    return None


def extract_first_heading(content: str) -> str | None:
    """Extract first markdown heading."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else None


def format_results(results: dict) -> str:
    """Format scan results as readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"ACS Project Scan — {results['project']}")
    lines.append(f"Date: {results['scan_date']}")
    lines.append("=" * 60)
    lines.append("")
    
    # Agents
    lines.append(f"## Agents Found: {len(results['agents'])}")
    for agent in results["agents"]:
        lines.append(f"  [{agent['id']}] {agent['name']} ({agent['type']})")
        if agent.get("role"):
            lines.append(f"      Role: {agent['role']}")
        lines.append(f"      Path: {agent['path']}")
    lines.append("")
    
    # Shared Resources
    lines.append(f"## Shared Resources: {len(results['shared_resources'])}")
    for r in results["shared_resources"]:
        flag = "⚠️ COLLISION" if r.get("collision") else ""
        lines.append(f"  📄 {r['path']} — touched by {r['touched_by']} {flag}")
    lines.append("")
    
    # Collision Zones
    lines.append(f"## ⚠️  Collision Zones: {len(results['collision_zones'])}")
    for c in results["collision_zones"]:
        lines.append(f"  🔴 {c['resource']} — agents: {c['agents']} — risk: {c['risk']}")
        lines.append(f"     → {c['resolution']}")
    lines.append("")
    
    # Unowned Resources
    lines.append(f"## ❌ Unowned Resources: {len(results['unowned_resources'])}")
    for r in results["unowned_resources"]:
        lines.append(f"  ⚡ {r['path']} — needs an owner")
    lines.append("")
    
    # Summary
    collision_count = len(results["collision_zones"])
    unowned_count = len(results["unowned_resources"])
    
    lines.append("## Summary")
    if collision_count == 0 and unowned_count == 0:
        lines.append("  ✅ No collisions or unowned resources detected.")
    else:
        lines.append(f"  🔴 {collision_count} collision zones — assign owners")
        lines.append(f"  ⚡ {unowned_count} unowned resources — register them")
    
    lines.append("")
    lines.append("Next step: Copy templates/AGENT_CONTRACT.md to the project root")
    lines.append("           and fill in owners for each resource listed above.")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_agents.py <project_path>")
        print("Example: python scan_agents.py ~/my-claude-code-project")
        sys.exit(1)
    
    project_root = Path(sys.argv[1]).resolve()
    if not project_root.exists():
        print(f"❌ Project path not found: {project_root}")
        sys.exit(1)
    
    print(f"🔍 Scanning project: {project_root}")
    print()
    
    results = scan_project(project_root)
    print(format_results(results))
    
    # Save JSON for programmatic use
    output_dir = project_root / ".acs"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "scan_result.json"
    output_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n💾 Machine-readable results: {output_path}")
    
    return results


if __name__ == "__main__":
    main()
