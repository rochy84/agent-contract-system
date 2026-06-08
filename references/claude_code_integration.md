# ACS + Claude Code Integration

> How to set up the Agent Contract System for Claude Code projects.

---

## Setup (5 minutes)

### 1. Create the contract registry

```bash
# Scan your project
python skills/agent-contract-system/scripts/scan_agents.py .

# Copy and fill in the template
cp skills/agent-contract-system/templates/AGENT_CONTRACT.md ./AGENT_CONTRACT.md

# Edit AGENT_CONTRACT.md — fill in owners for every resource
```

### 2. Inject the guard clause into every CLAUDE.md

For each `CLAUDE.md` in your project, prepend the guard clause:

```bash
# For the main project CLAUDE.md
cat skills/agent-contract-system/templates/guard_clause.md >> temp_guard.md
cat CLAUDE.md >> temp_guard.md
mv temp_guard.md CLAUDE.md

# For each agent in .claude/agents/
for agent_dir in .claude/agents/*/; do
  agent_md="$agent_dir/CLAUDE.md"
  if [ -f "$agent_md" ]; then
    cat skills/agent-contract-system/templates/guard_clause.md >> temp_guard.md
    cat "$agent_md" >> temp_guard.md
    mv temp_guard.md "$agent_md"
  fi
done
```

### 3. Add a checkpoint agent (optional but recommended)

Create `.claude/agents/contract-checkpoint/CLAUDE.md`:

```markdown
# Contract Checkpoint Agent

You are a contract compliance auditor. Your ONLY job is to validate that
other agents are following the Agent Contract Registry.

## Workflow

1. Read `AGENT_CONTRACT.md` — memorize the ownership rules
2. Check recent changes (git diff, file modification times)
3. For each changed resource:
   - Was the changing agent the owner or authorized writer?
   - Was the change logged in the Change Log?
   - Were reader agents notified?
4. Report any contract violations

## Output Format

```
ACS Checkpoint — [DATE]

✅ Compliant changes:
- [resource] by [agent] — owner, logged ✓, readers notified ✓

⚠️  Violations:
- [resource] by [agent] — NOT the owner. Owner is [owner].
- [resource] by [agent] — change not logged.
- [resource] by [agent] — readers not notified: [list].
```

## Schedule

Run this agent:
- Before any major deployment
- After any incident
- At least once per week
```

---

## Daily Workflow

### For Humans

1. When adding a new agent → run scan_agents.py, update AGENT_CONTRACT.md
2. When an agent's responsibilities change → update AGENT_CONTRACT.md
3. Weekly → run validate_contract.py, review results

### For Agents (automatic if guard clause is in CLAUDE.md)

1. Before writing any file → check AGENT_CONTRACT.md
2. After writing → log the change
3. If not the owner → open a change request (use templates/change_request.md)

---

## Common Claude Code Patterns

### Pattern 1: Single project, multiple CLAUDE.md files

```
my-project/
├── CLAUDE.md              ← Main agent (owns project config)
├── AGENT_CONTRACT.md       ← The registry
├── .claude/
│   └── agents/
│       ├── email-agent/
│       │   └── CLAUDE.md  ← Email agent (owns templates)
│       ├── amazon-agent/
│       │   └── CLAUDE.md  ← Amazon agent (owns listings)
│       └── analytics-agent/
│           └── CLAUDE.md  ← Analytics agent (owns reports, reads everything)
└── templates/
    └── emails/            ← Owned by email-agent
```

### Pattern 2: Multi-repo, shared resources

```
email-platform/            ← Repo 1
├── CLAUDE.md
├── AGENT_CONTRACT.md      ← Local registry
└── templates/

amazon-store/              ← Repo 2
├── CLAUDE.md
├── AGENT_CONTRACT.md      ← Local registry
└── listings/

shared-data/               ← Repo 3 (shared)
├── AGENT_CONTRACT.md      ← Cross-repo registry
└── segments/
```

For cross-repo resources, the shared-data AGENT_CONTRACT.md is the authority.
Each repo's local contract references it for cross-repo dependencies.

---

## Troubleshooting

### "Agent keeps ignoring the contract"

→ The guard clause might not be at the very top of CLAUDE.md. Claude Code prioritizes the first instructions. Make sure the guard clause is literally the first thing the agent reads.

### "Too many collision zones detected"

→ This is normal at first. The scan is conservative — it flags anything that *might* be shared. Assign owners and remove false positives. After the first pass, real collisions should drop.

### "Agents aren't logging changes"

→ Add the change log step to the guard clause output format. Make it concrete: "After any write, output: `ACS LOG: changed [resource] as [owner/writer]. Readers: [list]. Breaking: [yes/no]`"

---

## Migration from No Contract → Full Contract

Week 1: Run scan, create AGENT_CONTRACT.md, don't enforce yet. Just observe.
Week 2: Assign owners, inject guard clause with "warn but don't block" mode.
Week 3: Enable blocking for HIGH-risk resources. Warnings for MEDIUM.
Week 4: Full enforcement. Add checkpoint agent.
