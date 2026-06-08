# Agent Contract System (ACS)

> **Stop AI agents from breaking each other's work. One registry. Clear ownership. No more chaos.**

Multiple AI agents touching the same files, templates, databases, and configs? Agent A changes something Agent B depends on. No one knows who owns what. Changes collide. Stuff breaks silently.

**ACS solves this with a single source of truth: the Agent Contract Registry.**

## Quick Start

```bash
# 1. Scan your project
python scripts/scan_agents.py /path/to/your/project

# 2. Create the registry
cp templates/AGENT_CONTRACT.md /path/to/your/project/AGENT_CONTRACT.md
# Edit it — fill in owners for every resource

# 3. Inject the guard clause into every agent
cat templates/guard_clause.md >> /path/to/your/project/CLAUDE.md

# 4. Validate regularly
python scripts/validate_contract.py /path/to/your/project
```

## How It Works

1. **Scan** — discovers all AI agents and the shared resources they touch
2. **Register** — one file (`AGENT_CONTRACT.md`) defines who owns what
3. **Guard** — every agent checks the contract before making changes
4. **Validate** — weekly health checks catch violations before they break things

## The 4 Laws

1. **Check before changing** — read AGENT_CONTRACT.md before modifying any shared resource
2. **One owner, one truth** — every shared resource has exactly one owner
3. **Notify readers** — when a resource changes, all dependent agents are notified
4. **No silent breaks** — breaking changes are flagged and coordinated

## Supported Runtimes

- **Claude Code** — native CLAUDE.md injection + `.claude/agents/` discovery
- **OpenClaw** — skills, cron jobs, multi-agent workspaces
- **General** — any project with multiple AI agents touching shared files

## Structure

```
├── SKILL.md                          ← Core instructions
├── scripts/
│   ├── scan_agents.py                ← Discover agents & resources
│   └── validate_contract.py          ← Contract health scoring
├── templates/
│   ├── AGENT_CONTRACT.md             ← Blank registry (copy to project)
│   ├── AGENT_CONTRACT_EXAMPLE.md     ← Filled example (email + Amazon)
│   ├── guard_clause.md               ← System prompt injection
│   └── change_request.md             ← Cross-agent change requests
├── references/
│   ├── claude_code_integration.md    ← Claude Code setup guide
│   └── patterns.md                   ← Real collision patterns & fixes
└── assets/
    └── contract_schema.json          ← Machine-readable schema
```

## Example

See `templates/AGENT_CONTRACT_EXAMPLE.md` for a fully worked example with 8 agents managing an email marketing platform + Amazon store — email templates, customer segments, product listings, pricing, inventory, and external APIs.

## License

MIT
