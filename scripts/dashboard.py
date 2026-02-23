#!/usr/bin/env python3
"""
Nexus Automation — Dashboard
Real-time view of business pipeline and metrics.
"""

import json
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

class Dashboard:
    def __init__(self):
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        """Load all pipeline data."""
        data = {
            "leads": [],
            "outreach": [],
            "meetings": [],
            "deals": [],
            "clients": [],
            "case_studies": [],
            "invoices": [],
        }
        
        # Load leads from all lead files
        for filepath in PIPELINE_DIR.glob("leads_*.json"):
            with open(filepath) as f:
                data["leads"].extend(json.load(f))
        
        # Load other files
        for key in ["outreach", "meetings", "deals", "clients", "case_studies", "invoices"]:
            filepath = PIPELINE_DIR / f"{key}.json"
            if filepath.exists():
                with open(filepath) as f:
                    content = f.read().strip()
                    if content:
                        data[key] = json.loads(content)
        
        return data
    
    def render(self):
        """Render dashboard to console."""
        data = self.load_data()
        
        print("\n" + "="*60)
        print("🤖 NEXUS AUTOMATION DASHBOARD")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # Leads
        leads = data["leads"]
        hot = len([l for l in leads if l.get('score', {}).get('tier') == 'hot'])
        warm = len([l for l in leads if l.get('score', {}).get('tier') == 'warm'])
        pending_outreach = len([l for l in leads if l.get('outreach', {}).get('status') == 'pending'])
        
        print(f"\n📥 LEADS")
        print(f"   Total discovered: {len(leads)}")
        print(f"   HOT: {hot} | WARM: {warm}")
        print(f"   Awaiting outreach: {pending_outreach}")
        
        # Outreach
        outreach = data["outreach"]
        active_sequences = len([o for o in outreach if o.get('status') == 'active'])
        simulated_sequences = len([o for o in outreach if o.get('status') == 'simulated'])
        
        print(f"\n📤 OUTREACH")
        print(f"   Active sequences: {active_sequences}")
        print(f"   Simulated (dry run): {simulated_sequences}")
        
        # Meetings
        meetings = data["meetings"]
        print(f"\n📅 MEETINGS")
        print(f"   Booked: {len(meetings)}")
        
        # Deals
        deals = data["deals"]
        closed_won = [d for d in deals if d.get('status') == 'closed_won']
        total_pipeline = sum(d.get('value', 0) for d in deals)
        
        print(f"\n💰 DEALS")
        print(f"   In pipeline: {len(deals)}")
        print(f"   Closed-won: {len(closed_won)}")
        print(f"   Pipeline value: ${total_pipeline:,}")
        
        # Clients
        clients = data["clients"]
        active = [c for c in clients if c.get('status') == 'active']
        total_mrr = sum(c.get('mrr', 0) for c in active)
        
        print(f"\n👥 CLIENTS")
        print(f"   Active: {len(active)}")
        print(f"   Total MRR: ${total_mrr:,}")
        
        if active:
            print(f"\n   Client List:")
            for c in active:
                auto = c.get('automation', {})
                outcome = auto.get('outcome', {})
                print(f"   • {c['company']}: ${c['mrr']}/mo — {outcome.get('time_saved_weekly', '?')} hrs/week saved")
        
        # Case Studies
        case_studies = data["case_studies"]
        print(f"\n📚 CASE STUDIES")
        print(f"   Completed: {len(case_studies)}")
        
        if case_studies:
            print(f"\n   Recent Wins:")
            for cs in case_studies[-3:]:
                results = cs.get('results', {})
                print(f"   • {cs['client']}: {results.get('time_saved', 'N/A')}/week")
        
        # Invoices
        invoices = data["invoices"]
        pending_invoices = [i for i in invoices if i.get('status') == 'pending_manual_send']
        pending_amount = sum(i.get('total_due', 0) for i in pending_invoices)
        
        print(f"\n🧾 INVOICES")
        print(f"   Pending manual send: {len(pending_invoices)}")
        print(f"   Total pending: ${pending_amount:,}")
        
        # Actions
        print(f"\n⚡ ACTIONS NEEDED")
        actions = []
        
        if pending_outreach > 0:
            actions.append(f"Run outreach on {pending_outreach} pending leads")
        if len(meetings) > 0:
            actions.append(f"Process {len(meetings)} booked meetings (sales)")
        if len(pending_invoices) > 0:
            actions.append(f"Send {len(pending_invoices)} invoices manually")
        if not any([leads, outreach, deals, clients]):
            actions.append("Run full pipeline: python scripts/run_pipeline.py")
        
        if actions:
            for action in actions:
                print(f"   → {action}")
        else:
            print("   ✓ All caught up")
        
        print("\n" + "="*60)
        print("Commands:")
        print("  python scripts/run_pipeline.py  — Run full loop")
        print("  python scripts/lead_gen.py      — Find new leads")
        print("  python scripts/outreach.py      — Contact leads")
        print("  python scripts/sales.py         — Process meetings")
        print("  python scripts/fulfillment.py   — Build automations")
        print("  python scripts/ops.py --invoices — Generate invoices")
        print("="*60 + "\n")

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.render()
