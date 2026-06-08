# Agent Contract Registry — Example (Email Marketing + Amazon Store)

> ═══════════════════════════════════════════════════════════
> Single source of truth for all agents and shared resources.
> Managed by: Agent Contract System (ACS)
> Last updated: 2026-06-08
> ═══════════════════════════════════════════════════════════

---

## Agent Inventory

| ID | Agent Name | Role | Runtime | Owns | Reads/Writes | Last Review |
|----|-----------|------|---------|------|--------------|-------------|
| AGT-001 | Email Conversion Agent | Email copy & subject line optimization | claude-code | Email templates (body, subject, CTAs) | Reads: customer segments, brand guidelines. Writes: email templates. | 2026-06-08 |
| AGT-002 | Email Compliance Agent | CAN-SPAM & GDPR compliance review | claude-code | Email templates (legal footer, disclaimers) | Reads: email templates, privacy policy. Writes: email templates (footer only). | 2026-06-08 |
| AGT-003 | Amazon SEO Agent | Amazon listing optimization (title, bullets, description, backend keywords) | claude-code | Amazon listing content | Reads: competitor data, keyword research. Writes: listing content. | 2026-06-08 |
| AGT-004 | Amazon Pricing Agent | Dynamic pricing & offer management | claude-code | Prices, offers, promotions | Reads: competitor prices, inventory levels, listing content (read-only). Writes: prices, offers. | 2026-06-08 |
| AGT-005 | Amazon Inventory Agent | Stock level tracking & restock alerts | claude-code | Inventory quantities, restock triggers | Reads: sales velocity, supplier APIs. Writes: inventory counts. | 2026-06-08 |
| AGT-006 | Campaign Scheduler Agent | Email campaign scheduling & sending | claude-code | Campaign configs, send schedules | Reads: email templates, customer segments, sending limits. Writes: campaign configs. | 2026-06-08 |
| AGT-007 | Analytics Agent | Reporting, segmentation, performance dashboards | claude-code | Reports, customer segments | Reads: all data (read-only). Writes: reports, segment definitions. | 2026-06-08 |
| AGT-008 | Contract Checkpoint Agent | Contract compliance audit | claude-code | AGENT_CONTRACT.md | Reads: all project files (read-only). Writes: checkpoint reports. | 2026-06-08 |

---

## Shared Resources

### Files & Templates

| Resource | Path | Owner (Agent ID) | Writers | Readers | Description |
|----------|------|------------------|---------|---------|-------------|
| Welcome Email Template | templates/emails/welcome.html | AGT-001 (body), AGT-002 (footer) | AGT-001, AGT-002 | AGT-006, AGT-007 | New subscriber welcome series |
| Abandoned Cart Template | templates/emails/abandoned_cart.html | AGT-001 (body), AGT-002 (footer) | AGT-001, AGT-002 | AGT-006, AGT-007 | Cart recovery emails |
| Weekly Newsletter Template | templates/emails/newsletter.html | AGT-001 (body), AGT-002 (footer) | AGT-001, AGT-002 | AGT-006, AGT-007 | Weekly digest |
| Email Sending Config | config/sending.json | AGT-006 | AGT-006 | AGT-001, AGT-002, AGT-007 | Rate limits, sending windows, domain config |
| Brand Guidelines | config/brand_guidelines.md | AGT-001 | AGT-001 | AGT-002, AGT-003 | Tone, voice, style rules |
| Amazon Listing Batch File | listings/batch_update.csv | AGT-008 (orchestrator) | AGT-003, AGT-004, AGT-005 | AGT-007 | Staging files: batch_update_seo.csv, batch_update_prices.csv, batch_update_inventory.csv |

### Data Stores

| Resource | Connection/Path | Owner (Agent ID) | Writers | Readers | Description |
|----------|----------------|------------------|---------|---------|-------------|
| Customer Preferences DB | customers.db (email_preferences) | AGT-007 | AGT-007 | AGT-001, AGT-006 (read-only) | Email opt-in, frequency, interests |
| Product Catalog | products.db | AGT-003 | AGT-003, AGT-004 | AGT-005, AGT-007 | Product details, categories |
| Inventory DB | inventory.db | AGT-005 | AGT-005 | AGT-003, AGT-004, AGT-007 (read-only) | Stock levels, restock dates |

### Logical Entities

| Resource | Definition Location | Owner (Agent ID) | Writers | Readers | Description |
|----------|-------------------|------------------|---------|---------|-------------|
| VIP Customer Segment | segments/definitions.json (vip) | AGT-007 | AGT-007 | AGT-001, AGT-006 | >$500 lifetime spend, active in last 30 days |
| At-Risk Segment | segments/definitions.json (at_risk) | AGT-007 | AGT-007 | AGT-001, AGT-006 | No purchase in 60+ days, previously active |
| New Customer Segment | segments/definitions.json (new) | System (date-based) | None | AGT-001, AGT-006 | First purchase <30 days ago |
| Pricing Rules | config/pricing_rules.json | AGT-004 | AGT-004 | AGT-003, AGT-007 | Min/max margins, competitor matching thresholds |

### External Integrations

| Resource | API/Service | Owner (Agent ID) | Writers | Readers | Description |
|----------|------------|------------------|---------|---------|-------------|
| Email Sending API | SendGrid / SES | AGT-006 | AGT-006 | AGT-001, AGT-002, AGT-007 | Outbound email delivery |
| Amazon SP-API | sellingpartnerapi.amazon.com | AGT-003 | AGT-003, AGT-004, AGT-005 | AGT-007 | Product listings, pricing, inventory |
| Supplier Stock API | supplier-api.example.com | AGT-005 | AGT-005 | AGT-007 | Real-time supplier inventory |

---

## Dependency Map

| Agent ID | Depends On (Resource) | Type | Impact If Resource Changes |
|----------|----------------------|------|---------------------------|
| AGT-006 | Email templates (AGT-001, AGT-002) | Content | Campaigns send wrong content |
| AGT-006 | Customer segments (AGT-007) | Targeting | Wrong audience receives campaign |
| AGT-006 | Sending config | Timing | Deliverability issues, rate limiting |
| AGT-003 | Inventory levels (AGT-005) | Availability | Listing shows out-of-stock incorrectly |
| AGT-004 | Inventory levels (AGT-005) | Pricing | Prices not adjusted for stock levels |
| AGT-004 | Competitor data | Pricing | Stale or uncompetitive prices |
| AGT-001 | Brand guidelines | Content | Off-brand copy |
| AGT-001 | Customer segments (AGT-007) | Personalization | Irrelevant content to wrong segment |

---

## Collision Zones

| Resource | Agents Touching | Risk | Resolution |
|----------|----------------|------|------------|
| Email templates (body) | AGT-001, AGT-002 | MEDIUM | Partitioned: AGT-001 owns body, AGT-002 owns footer. Merge rules defined. |
| batch_update.csv | AGT-003, AGT-004, AGT-005 | HIGH | Orchestrator pattern: agents write to staging files. AGT-008 merges. |
| Brand guidelines | AGT-001, AGT-002, AGT-003 | LOW | AGT-001 is sole owner. Others read-only. |

---

## Change Log

| Date | Agent ID | Resource Changed | What Changed | Readers Notified | Reviewer |
|------|----------|-----------------|--------------|-----------------|----------|
| 2026-06-08 | AGT-007 | VIP Customer Segment | Threshold updated: >$500 → >$750 lifetime spend. ⚠️ BREAKING | AGT-001, AGT-006 notified | Human |
| 2026-06-07 | AGT-001 | Welcome Email Template | Subject line A/B test variant added | AGT-006 notified | Human |

---

## Rules (The 4 Laws)

1. **Check before changing.** Read this file before modifying any shared resource.
2. **One owner, one truth.** Every shared resource must have exactly one owner ID (or partitioned co-ownership).
3. **Notify readers.** When a resource changes, list all reader agents in the change log and notify them.
4. **No silent breaks.** If a change might break a dependent agent, flag it as ⚠️ BREAKING.

---

## Contract Health

| Metric | Target | Current |
|--------|--------|---------|
| Resources with owners | 100% | 100% |
| Resources with collision zones resolved | 100% | 100% |
| Change log entries with reader notifications | 100% | 100% |
| Agents registered | All (8) | 8 |
| Last validation | Within 7 days | 2026-06-08 |

---

_Registry managed by: Agent Contract System_
_Next validation: 2026-06-15_
