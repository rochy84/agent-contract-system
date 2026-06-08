# Agent Contract Registry

> ═══════════════════════════════════════════════════════════
> Single source of truth for all agents and shared resources.
> Managed by: Agent Contract System (ACS)
> Last updated: [DATE]
> ═══════════════════════════════════════════════════════════

---

## Agent Inventory

List every AI agent that runs in this project. One row per agent.

| ID | Agent Name | Role | Runtime | Owns | Reads/Writes | Last Review |
|----|-----------|------|---------|------|--------------|-------------|
| AGT-001 | | | | | | |
| AGT-002 | | | | | | |

**Runtime options:** `claude-code`, `openclaw`, `langchain`, `custom-script`, `manual`

---

## Shared Resources

### Files & Templates

| Resource | Path | Owner (Agent ID) | Writers | Readers | Description |
|----------|------|------------------|---------|---------|-------------|
| | | | | | |

### Data Stores

| Resource | Connection/Path | Owner (Agent ID) | Writers | Readers | Description |
|----------|----------------|------------------|---------|---------|-------------|
| | | | | | |

### Logical Entities

| Resource | Definition Location | Owner (Agent ID) | Writers | Readers | Description |
|----------|-------------------|------------------|---------|---------|-------------|
| | | | | | |

### External Integrations

| Resource | API/Service | Owner (Agent ID) | Writers | Readers | Description |
|----------|------------|------------------|---------|---------|-------------|
| | | | | | |

---

## Dependency Map

Which agents depend on which resources?

| Agent ID | Depends On (Resource) | Type | Impact If Resource Changes |
|----------|----------------------|------|---------------------------|
| | | | |

---

## Collision Zones

Resources touched by multiple agents that have NO owner. These are time bombs.

| Resource | Agents Touching | Risk | Resolution |
|----------|----------------|------|------------|
| | | | |

---

## Change Log

| Date | Agent ID | Resource Changed | What Changed | Readers Notified | Reviewer |
|------|----------|-----------------|--------------|-----------------|----------|
| | | | | | |

---

## Rules (The 4 Laws)

1. **Check before changing.** Read this file before modifying any shared resource.
2. **One owner, one truth.** Every shared resource must have exactly one owner ID.
3. **Notify readers.** When a resource changes, list all reader agents in the change log and notify them.
4. **No silent breaks.** If a change might break a dependent agent, flag it in the change log as ⚠️ BREAKING.

---

## Contract Health

| Metric | Target | Current |
|--------|--------|---------|
| Resources with owners | 100% | |
| Resources with collision zones resolved | 100% | |
| Change log entries with reader notifications | 100% | |
| Agents registered | All | |
| Last validation | Within 7 days | |

---

_Registry managed by: Agent Contract System_
_Next validation: [DATE]_
