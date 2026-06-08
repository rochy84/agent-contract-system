---
name: agent-contract-system
description: "Prevent multi-agent collisions with a shared-resource contract registry. Agentic project coordination (Claude Code, OpenClaw, etc.)."
---

# Agent Contract System (ACS)

> **Stop agents from breaking each other's work. One registry. Clear ownership. No more chaos.**
> **Version: 1.0**

---

## The Problem

Multiple AI agents touch shared resources (files, templates, databases, configs). Agent A changes something Agent B depends on. No one knows who owns what. Changes collide. Stuff breaks silently.

ACS solves this with a **single source of truth**: the Agent Contract Registry.

## Quick Start

### 1. Scan the project

```bash
python scripts/scan_agents.py /path/to/project
```

This discovers agents, shared resources, and potential collision points (files read/written by multiple agents).

### 2. Create the registry

Use the generated scan results and the template at `templates/AGENT_CONTRACT.md` to create a contract registry at the project root.

### 3. Inject the contract check

Add the guard clause from `templates/guard_clause.md` to every agent's system prompt / CLAUDE.md.

### 4. Validate regularly

```bash
python scripts/validate_contract.py /path/to/project
```

Flags: resources with no owner, resources with conflicting owners, agents touching resources they don't own.

---

## Core Concepts

### Resources

Anything shared between agents:

- Files (templates, configs, data, code)
- Data stores (database tables, API endpoints, vector stores)
- Logical entities (customer segments, pricing rules, campaign configs)
- External integrations (email sends, Amazon API, payment gateways)

### Ownership Modes

| Mode | Meaning | Conflict Rule |
|------|---------|---------------|
| **Owner** | This agent is the authority; changes don't need external approval | Only one owner per resource (or explicit co-ownership with merge rules) |
| **Writer** | Can modify, but must notify owners | Owners can veto |
| **Reader** | Read-only access | No write allowed |
| **None** | No access (not listed) | Must request access |

### Contract Rules (The 4 Laws)

1. **Check before changing.** Before modifying any shared resource, read AGENT_CONTRACT.md and verify you have the right.
2. **One owner, one truth.** Every shared resource must have exactly one owner (or defined co-ownership).
3. **Notify readers.** When a resource changes, notify all reader agents so they can validate their assumptions.
4. **No silent breaks.** If a change might break another agent, pause and coordinate. Don't just push it.

---

## File Structure

```
agent-contract-system/
├── SKILL.md                          ← This file
├── templates/
│   ├── AGENT_CONTRACT.md             ← The registry template (copy to project root)
│   ├── guard_clause.md               ← System prompt injection for agents
│   └── change_request.md             ← Template for cross-agent change requests
├── scripts/
│   ├── scan_agents.py                ← Discover agents and shared resources
│   └── validate_contract.py          ← Check registry for violations
├── references/
│   ├── patterns.md                   ← Common collision patterns and fixes
│   └── claude_code_integration.md    ← Claude Code-specific setup
└── assets/
    └── contract_schema.json          ← Machine-readable schema
```

---

## Integration: Claude Code

### Step 1: Create AGENT_CONTRACT.md at the project root

Copy `templates/AGENT_CONTRACT.md` and fill it in based on the scan results.

### Step 2: Add the guard clause to each agent's CLAUDE.md

Insert `templates/guard_clause.md` at the top of every `CLAUDE.md` file.

### Step 3: Run the checkpoint agent periodically

Use the checkpoint prompt from `references/claude_code_integration.md` as a periodic or pre-commit review.

---

## Integration: OpenClaw

Same concept applies to OpenClaw skills and agents. The contract registry maps to skills/agents touching the same files, databases, or external services.

---

## When to Run

| Trigger | Action |
|---------|--------|
| New agent added | Scan → register it and its resources |
| Agent prompt changed | Check if resource ownership changed |
| Before major changes | Validate contract for collisions |
| After incidents (breakage) | Post-mortem: was the contract violated? |
| Weekly | Validate contract health |

---

## Philosophy

- **Practical, not bureaucratic.** One file. Clear rules. No spreadsheets.
- **Prevention over recovery.** A 10-second contract check beats hours of debugging.
- **Agents are team members.** They need boundaries like humans do.
- **Domain-agnostic.** Works for email marketing, Amazon stores, SaaS, anything with multiple agents.

---

## Key Principles

1. **Single source of truth** — AGENT_CONTRACT.md is the authority
2. **Explicit ownership** — every shared resource has one owner
3. **Change notification** — readers know when their dependencies change
4. **Lightweight by design** — one file, simple rules, no infrastructure
5. **Pre-flight, not post-mortem** — check before breaking
