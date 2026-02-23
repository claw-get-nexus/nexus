---
name: nexus-automation
description: Nexus Automation — Autonomous business automation agency. Run lead gen, outreach, sales, fulfillment, and ops without human intervention. Use when building or operating a self-running service business that sells automation to other businesses.
---

# Nexus Automation

**Tagline:** We built an autonomous business. Want yours?

Autonomous agency that finds businesses with operational pain, sells them automation solutions, delivers working systems, and manages the entire lifecycle — all via AI agents.

## Business Model

- **Freemium proof-of-value:** 2-week free pilot
- **Transparent AI:** Clients know agents do the work — that's the pitch
- **Recursive case studies:** Every client becomes marketing material

## Pricing Tiers

| Tier | Monthly | Deliverable |
|------|---------|-------------|
| Pilot | $0 | Working automation + 2 weeks runtime |
| Starter | $500 | 1 workflow, email support |
| Growth | $2,000 | 5 workflows, priority, weekly optimization |
| Enterprise | $5,000 | Unlimited, SLA, dedicated cluster |

## Agent Swarm

| Agent | Function | Trigger |
|-------|----------|---------|
| **Lead Gen** | Scrape job boards, Twitter, Reddit for pain signals | Cron: hourly |
| **Outreach** | Personalized email sequences | New HOT leads |
| **Sales** | Discovery calls, qualification, closing | Booked meetings |
| **Fulfillment** | Build client automation systems | Closed deals |
| **Ops** | Invoice requests, case studies, reporting | Cron: daily |

## Data Sources

- **Indeed/Greenhouse/Lever** — Job postings for operational roles
- **Twitter/X** — Public complaints about manual work
- **Reddit** — r/smallbusiness, r/operations pain threads
- **Company websites** — Growth signals, team pages

## Quick Commands

```bash
# Run full pipeline (dry mode)
python scripts/run_pipeline.py --mock

# Individual agents
python scripts/lead_gen.py --source all
python scripts/outreach.py --tier hot --dry-run
python scripts/dashboard.py

# Generate invoice request for manual billing
python scripts/ops.py --invoice-due
```

## Configuration

Edit `references/config.json` for business rules, pricing, scoring thresholds.

## Pipeline Files

All data in `assets/pipeline/`:
- `leads_*.json` — Scored leads
- `outreach.json` — Active sequences
- `deals.json` — Sales pipeline
- `clients.json` — Active clients
- `invoices.json` — Pending invoice requests (for manual processing)
- `case_studies.json` — Completed projects

## Human Override Points

- Deals >$5K/month (configurable)
- Custom fulfillment requests
- Client escalations
- System errors

Set `auto_approve: true` to disable (not recommended).
