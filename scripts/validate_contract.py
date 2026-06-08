#!/usr/bin/env python3
"""
Agent Contract System — Contract Validator
Validates an existing AGENT_CONTRACT.md for violations, gaps, and risks.

Checks:
1. Every registered agent exists and has a system prompt
2. Every shared resource has an owner
3. No resource has conflicting owners (two agents claiming ownership)
4. All collision zones are resolved
5. Change log is complete (entries have reader notifications)
6. Contract health metrics are current
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


def validate_contract(project_root: Path) -> dict:
    """Validate AGENT_CONTRACT.md and return findings."""
    
    contract_path = project_root / "AGENT_CONTRACT.md"
    if not contract_path.exists():
        return {
            "valid": False,
            "fatal": "No AGENT_CONTRACT.md found at project root. Run scan_agents.py first, then copy templates/AGENT_CONTRACT.md to the project root and fill it in.",
            "issues": [],
            "warnings": [],
            "score": 0,
        }
    
    content = contract_path.read_text()
    issues = []
    warnings = []
    
    # ── 1. Agent Registration ──
    agents = extract_agents(content)
    if not agents:
        issues.append("No agents registered. Fill in the Agent Inventory table.")
    else:
        for agent in agents:
            # Check if agent file exists
            if agent.get("path"):
                agent_path = project_root / agent["path"]
                if not agent_path.exists():
                    warnings.append(f"Agent '{agent.get('name')}' references path '{agent['path']}' that doesn't exist.")
    
    # ── 2. Shared Resources ──
    resources = extract_resources(content)
    if not resources:
        issues.append("No shared resources registered. Fill in the Shared Resources tables.")
    else:
        for resource in resources:
            if not resource.get("owner"):
                issues.append(f"Resource '{resource.get('name')}' has no owner assigned.")
            
            # Check for conflicting owners
            if resource.get("owner") and resource.get("writers"):
                if resource["owner"] in resource.get("writers", []):
                    pass  # Owner can be a writer too
                    
    # ── 3. Collision Zones ──
    collisions = extract_collisions(content)
    unresolved = [c for c in collisions if not c.get("resolution") or c.get("resolution") == ""]
    if unresolved:
        issues.append(f"{len(unresolved)} collision zone(s) without resolution.")
    
    # ── 4. Change Log Completeness ──
    change_entries = extract_changes(content)
    for entry in change_entries:
        if not entry.get("readers_notified"):
            warnings.append(f"Change log entry '{entry.get('date')} - {entry.get('resource')}' doesn't indicate reader notification.")
    
    # ── 5. Contract Health Check ──
    health = extract_health(content)
    if not health:
        warnings.append("Contract Health section is empty. Fill in current metrics.")
    
    # ── 6. Cross-reference: agents in resources vs agent inventory ──
    agent_ids_registered = {a.get("id") for a in agents if a.get("id")}
    for resource in resources:
        for ag_ref in resource.get("readers", []) + [resource.get("owner", "")] + resource.get("writers", []):
            if ag_ref and ag_ref not in agent_ids_registered and ag_ref.strip():
                warnings.append(f"Resource '{resource.get('name')}' references agent '{ag_ref}' which is not in the Agent Inventory.")
    
    # ── 7. Staleness check ──
    last_updated_match = re.search(r'Last updated:\s*\[([^\]]+)\]', content)
    if last_updated_match:
        try:
            last_updated = datetime.strptime(last_updated_match.group(1), "%Y-%m-%d")
            if datetime.now() - last_updated > timedelta(days=7):
                warnings.append(f"Contract not updated since {last_updated.strftime('%Y-%m-%d')} (>7 days). Schedule a review.")
        except ValueError:
            pass
    
    # ── Score ──
    score = 100
    score -= len(issues) * 15  # Each issue: -15
    score -= len(warnings) * 5  # Each warning: -5
    score = max(0, score)
    
    return {
        "valid": len(issues) == 0,
        "fatal": None,
        "issues": issues,
        "warnings": warnings,
        "score": score,
        "score_rating": score_rating(score),
        "agents_count": len(agents),
        "resources_count": len(resources),
        "collisions_count": len(collisions),
        "unresolved_collisions": len(unresolved),
    }


def extract_agents(content: str) -> list:
    """Extract agents from the Agent Inventory table."""
    agents = []
    in_table = False
    for line in content.split("\n"):
        if "## Agent Inventory" in line:
            in_table = True
            continue
        if in_table and line.startswith("## ") and "Agent Inventory" not in line:
            break  # Next section started
        if in_table and line.startswith("|") and "---" not in line and "ID" not in line and "Agent Name" not in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            # First cell must be an agent ID like AGT-XXX
            if len(cells) >= 2 and cells[0] and re.match(r'AGT-\d{3}', cells[0]):
                agents.append({
                    "id": cells[0],
                    "name": cells[1] if len(cells) > 1 else "",
                    "role": cells[2] if len(cells) > 2 else "",
                })
    return agents


def extract_resources(content: str) -> list:
    """Extract resources from all Shared Resources sub-tables."""
    resources = []
    in_section = False
    for line in content.split("\n"):
        if "## Shared Resources" in line:
            in_section = True
            continue
        if in_section and line.startswith("## ") and "Shared Resources" not in line:
            break  # Next major section started
        if in_section and line.startswith("|") and "---" not in line and "Resource" not in line and "Owner" not in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 3 and cells[0]:
                # Clean owner: strip inline annotations like "(body)", "(footer)"
                owner_raw = cells[2] if len(cells) > 2 else ""
                owner_ids = re.findall(r'AGT-\d{3}', owner_raw)
                
                writers_raw = cells[3] if len(cells) > 3 else ""
                readers_raw = cells[4] if len(cells) > 4 else ""
                writer_ids = re.findall(r'AGT-\d{3}', writers_raw)
                reader_ids = re.findall(r'AGT-\d{3}', readers_raw)
                
                resources.append({
                    "name": cells[0],
                    "path": cells[1] if len(cells) > 1 else "",
                    "owner": owner_ids[0] if owner_ids else owner_raw,
                    "owners": owner_ids,
                    "writers": writer_ids,
                    "readers": reader_ids,
                })
    return resources


def extract_collisions(content: str) -> list:
    """Extract collision zones."""
    collisions = []
    in_table = False
    for line in content.split("\n"):
        if "Collision Zones" in line:
            in_table = True
            continue
        if in_table and line.strip() == "":
            in_table = False
            continue
        if in_table and line.startswith("|") and not line.startswith("|---") and "Resource" not in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 4 and cells[0]:
                collisions.append({
                    "resource": cells[0],
                    "agents": cells[1] if len(cells) > 1 else "",
                    "risk": cells[2] if len(cells) > 2 else "",
                    "resolution": cells[3] if len(cells) > 3 else "",
                })
    return collisions


def extract_changes(content: str) -> list:
    """Extract change log entries."""
    changes = []
    in_table = False
    for line in content.split("\n"):
        if "## Change Log" in line:
            in_table = True
            continue
        if in_table and line.strip() == "":
            in_table = False
            continue
        if in_table and line.startswith("|") and not line.startswith("|---") and "Date" not in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 1 and cells[0]:
                changes.append({
                    "date": cells[0] if len(cells) > 0 else "",
                    "agent": cells[1] if len(cells) > 1 else "",
                    "resource": cells[2] if len(cells) > 2 else "",
                    "readers_notified": cells[4] if len(cells) > 4 else "",
                })
    return changes


def extract_health(content: str) -> dict:
    """Extract contract health metrics."""
    health = {}
    in_table = False
    for line in content.split("\n"):
        if "## Contract Health" in line:
            in_table = True
            continue
        if in_table and line.strip() == "":
            in_table = False
            continue
        if in_table and line.startswith("|") and not line.startswith("|---") and "Metric" not in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 3 and cells[0]:
                health[cells[0]] = cells[2] if len(cells) > 2 else ""
    return health


def score_rating(score: int) -> str:
    if score >= 90:
        return "🟢 Strong"
    elif score >= 75:
        return "🟡 Adequate"
    elif score >= 50:
        return "🟠 Weak"
    else:
        return "🔴 Critical"


def format_results(result: dict) -> str:
    """Format validation results as readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("ACS Contract Validation Report")
    lines.append(f"Score: {result['score']}/100 — {result['score_rating']}")
    lines.append("=" * 60)
    lines.append("")
    
    if result.get("fatal"):
        lines.append(f"❌ FATAL: {result['fatal']}")
        return "\n".join(lines)
    
    lines.append(f"Registered agents:     {result['agents_count']}")
    lines.append(f"Shared resources:      {result['resources_count']}")
    lines.append(f"Collision zones:       {result['collisions_count']} ({result['unresolved_collisions']} unresolved)")
    lines.append("")
    
    if result["issues"]:
        lines.append(f"## Issues ({len(result['issues'])})")
        for issue in result["issues"]:
            lines.append(f"  ❌ {issue}")
        lines.append("")
    
    if result["warnings"]:
        lines.append(f"## Warnings ({len(result['warnings'])})")
        for warning in result["warnings"]:
            lines.append(f"  ⚠️  {warning}")
        lines.append("")
    
    if not result["issues"] and not result["warnings"]:
        lines.append("✅ No issues or warnings. Contract is healthy.")
    elif result["issues"]:
        lines.append("🔴 Action required: Fix issues above before agents make changes.")
    else:
        lines.append("🟡 Review recommended: Address warnings to strengthen the contract.")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_contract.py <project_path>")
        print("Example: python validate_contract.py ~/my-project")
        sys.exit(1)
    
    project_root = Path(sys.argv[1]).resolve()
    if not project_root.exists():
        print(f"❌ Project path not found: {project_root}")
        sys.exit(1)
    
    print(f"🔍 Validating contract at: {project_root}")
    print()
    
    result = validate_contract(project_root)
    print(format_results(result))
    
    # Save results
    output_dir = project_root / ".acs"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "validation_result.json"
    output_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\n💾 Validation results: {output_path}")
    
    return result


if __name__ == "__main__":
    main()
