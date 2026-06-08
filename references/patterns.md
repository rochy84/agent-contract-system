# Common Collision Patterns & Fixes

> Real-world patterns of multi-agent collisions and how the contract prevents them.

---

## Pattern 1: The Template Tug-of-War

**Scenario:** Agent A (Conversion Optimizer) rewrites email subject lines for open rates. Agent B (Compliance) rewrites the same templates to add legal footers. They overwrite each other.

**Why it happens:** No ownership partition. Both think the whole template is theirs.

**Contract fix:**
```
Resource: welcome_email.html
Owner: Conversion Agent (body, subject, CTAs)
Co-Owner: Compliance Agent (footer, legal disclaimers)
Rule: Conversion Agent writes first. Compliance Agent reviews and adds footer.
      Changes to shared sections require both to approve.
```

**Key insight:** "Owner" doesn't always mean one agent. It can mean **partitioned ownership** — each agent owns a section.

---

## Pattern 2: The Drifting Definition

**Scenario:** Analytics Agent redefines "VIP customer" (from >$500 spend to >$1000). Campaign Agent is still sending VIP campaigns to the old segment. Half the emails go to the wrong people.

**Why it happens:** Segment definitions changed without notifying consumers.

**Contract fix:**
```
Resource: VIP Customer Segment
Owner: Analytics Agent (defines the segment)
Readers: Campaign Agent, Retention Agent, Report Generator
Rule: Definition changes must be logged as ⚠️ BREAKING.
      All reader agents must re-validate before next run.
      Previous definition retained for 48h as fallback.
```

---

## Pattern 3: The Conflicting Config

**Scenario:** Admin Agent changes the email-sending rate limit in the config file (from 100/min to 50/min to avoid spam flags). Delivery Agent was already mid-send and suddenly can't deliver on time. Scheduled campaign fails silently.

**Why it happens:** Config changes have blast radius. No notification.

**Contract fix:**
```
Resource: config/sending.json
Owner: Admin Agent
Readers: Delivery Agent, Campaign Agent, Analytics Agent
Rule: Rate limit changes must be announced 1h before taking effect.
      Delivery Agent must acknowledge before config is applied.
```

---

## Pattern 4: The Write-Only Chaos

**Scenario:** SEO Agent updates Amazon listing titles. Pricing Agent updates prices. Both write to the same batch file. The last one to write wins — one change is silently lost.

**Why it happens:** Shared write target with no merge strategy.

**Contract fix:**
```
Resource: listings/batch_update.csv
Owner: Listing Orchestrator Agent (merge and validate)
Writers: SEO Agent, Pricing Agent, Inventory Agent
Rule: Writers write to their own staging files (e.g., batch_update_seo.csv).
      Listing Orchestrator merges, resolves conflicts, pushes final.
      No agent writes directly to batch_update.csv except the orchestrator.
```

---

## Pattern 5: The Database Collision

**Scenario:** Agent A reads customer data, processes it, and writes results back. Agent B reads the same data, modifies it differently, and writes. Both think they have the latest data. Data corruption.

**Why it happens:** No locking, no versioning, no "last read" tracking.

**Contract fix:**
```
Resource: customers.db (table: email_preferences)
Owner: Preferences Agent
Readers: Campaign Agent, Analytics Agent (read-only)
Rule: Only Preferences Agent writes to email_preferences.
      Other agents request changes via change_request.md.
      Preferences Agent processes requests in order.
```

---

## Pattern 6: The Prompt Mutation

**Scenario:** Agent A's CLAUDE.md is updated to handle a new edge case. The change accidentally removes a rule that Agent B depended on (via a shared reference file). Agent B starts behaving differently.

**Why it happens:** Agent prompts are resources too. Prompt changes can break dependent agents.

**Contract fix:**
```
Resource: CLAUDE.md (main agent)
Owner: Main Agent
Readers: Email Agent, Amazon Agent (reference shared rules)
Rule: Shared rules extracted to shared_rules.md.
      Main agent CLAUDE.md references shared_rules.md.
      Changes to shared_rules.md require all reader agents to review.
```

---

## General Principles

1. **Partition when you can.** One owner per logical section, not per file.
2. **Stage when you can't partition.** Writers write to staging areas. An orchestrator merges.
3. **Notify on shared writes.** If two agents must write to the same target, both must log and notify.
4. **Version definitions.** Segments, configs, rules — anything that agents depend on for decisions.
5. **The orchestrator pattern.** When in doubt, add a lightweight orchestrator agent whose only job is to merge and validate.

---

## Red Flags (Immediate Action Needed)

- Any resource touched by 3+ agents with no owner
- Any resource where agents alternate writing to the same file
- Any segment/rule/config definition change without reader notification
- Any agent that writes to a resource listed under a different agent's "Owns"
