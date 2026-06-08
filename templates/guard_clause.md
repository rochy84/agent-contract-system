# Guard Clause — Agent Contract Check

> Insert this at the TOP of every agent's system prompt / CLAUDE.md file.

---

## 🛡️ Resource Contract Rule

Before you modify ANY file, template, database record, configuration, or logical entity in this project:

1. **Read `AGENT_CONTRACT.md`** at the project root
2. **Find the resource** you want to modify in the Shared Resources tables
3. **Check your access:**
   - If you are the **Owner**: proceed. Log the change after.
   - If you are a **Writer**: proceed, but notify the Owner in the change log.
   - If you are a **Reader only**: STOP. You do not have write access. Open a change request instead.
   - If the resource is **not listed**: STOP. It hasn't been registered. Ask a human to register it.
4. **After changing**: add an entry to the Change Log with what changed, your Agent ID, and whether it's breaking.
5. **If the resource has readers**: notify them that the resource changed.

### Quick Self-Check

Before executing any write operation, ask yourself:

```
✅ Is this resource registered in AGENT_CONTRACT.md?
✅ Am I the owner or an authorized writer?
✅ Will this break any dependent agent?
✅ Have I logged the change?
✅ Have I notified readers?
```

**If you can't answer "yes" to all five, stop and flag it.**
