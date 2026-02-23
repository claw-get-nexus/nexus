#!/usr/bin/env python3
"""
Nexus Automation — Ops Agent
Handles reporting, invoice requests, and business intelligence.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from notifier import Notifier

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

def load_config():
    with open(SKILL_DIR / "references" / "config.json") as f:
        return json.load(f)

class OpsAgent:
    def __init__(self):
        self.config = load_config()
        self.notifier = Notifier()
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_pipeline(self) -> Dict:
        """Load all pipeline data."""
        data = {
            "leads": [],
            "outreach": [],
            "deals": [],
            "clients": [],
            "case_studies": [],
        }
        
        # Load leads
        for filepath in PIPELINE_DIR.glob("leads_*.json"):
            with open(filepath) as f:
                data["leads"].extend(json.load(f))
        
        # Load other files
        for key in ["outreach", "deals", "clients", "case_studies"]:
            filepath = PIPELINE_DIR / f"{key}.json"
            if filepath.exists():
                with open(filepath) as f:
                    content = f.read().strip()
                    if content:
                        data[key] = json.loads(content)
        
        return data
    
    def generate_invoice_requests(self, clients: List[Dict]) -> List[Dict]:
        """Generate invoice requests for manual billing."""
        invoices = []
        
        for client in clients:
            if client.get('status') != 'active':
                continue
            
            invoice = {
                "id": f"inv_{client['id']}_{datetime.now().strftime('%Y%m')}",
                "generated_at": datetime.now().isoformat(),
                "status": "pending_manual_send",
                "recipient": {
                    "company": client['company'],
                    "contact_name": client['contact']['name'],
                    "contact_email": f"finance@{client['company'].lower().replace(' ', '')}.com",  # Placeholder
                },
                "line_items": [
                    {
                        "description": f"Nexus Automation — {client['tier'].title()} Tier",
                        "period": f"{datetime.now().strftime('%B %Y')}",
                        "amount": client['mrr'],
                    }
                ],
                "total_due": client['mrr'],
                "due_date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                "notes": f"Monthly service fee for {client['company']}. Automation type: {client['automation']['type']}. Client since {client['started_at'][:10]}.",
            }
            invoices.append(invoice)
        
        return invoices
    
    def generate_report(self) -> Dict:
        """Generate business performance report."""
        data = self.load_pipeline()
        
        # Calculate metrics
        leads = data['leads']
        hot_leads = len([l for l in leads if l.get('score', {}).get('tier') == 'hot'])
        warm_leads = len([l for l in leads if l.get('score', {}).get('tier') == 'warm'])
        
        deals = data['deals']
        closed_deals = [d for d in deals if d.get('status') == 'closed_won']
        total_deal_value = sum(d['value'] for d in closed_deals)
        
        clients = data['clients']
        active_clients = [c for c in clients if c.get('status') == 'active']
        total_mrr = sum(c['mrr'] for c in active_clients)
        
        case_studies = data['case_studies']
        
        # Calculate conversion rates
        lead_to_deal = len(closed_deals) / len(leads) * 100 if leads else 0
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_leads": len(leads),
                "hot_leads": hot_leads,
                "warm_leads": warm_leads,
                "deals_closed": len(closed_deals),
                "total_deal_value": total_deal_value,
                "active_clients": len(active_clients),
                "total_mrr": total_mrr,
                "case_studies": len(case_studies),
            },
            "conversion_rates": {
                "lead_to_deal": round(lead_to_deal, 1),
            },
            "active_clients": [
                {
                    "company": c['company'],
                    "tier": c['tier'],
                    "mrr": c['mrr'],
                    "automation_type": c['automation']['type'],
                    "time_saved": c['automation']['outcome']['time_saved_weekly'],
                }
                for c in active_clients
            ],
            "recent_case_studies": [
                {
                    "client": cs['client'],
                    "challenge": cs['challenge'][:50] + '...',
                    "results": cs['results'],
                }
                for cs in case_studies[-3:]
            ],
        }
    
    def run(self, generate_invoices: bool = False):
        """Run ops reporting."""
        print("📊 Nexus Automation — Ops Agent")
        print("=" * 50)
        
        data = self.load_pipeline()
        report = self.generate_report()
        
        print(f"\n  📈 BUSINESS REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"  {'='*46}")
        
        summary = report['summary']
        print(f"\n  📥 LEADS")
        print(f"     Total: {summary['total_leads']}")
        print(f"     Hot: {summary['hot_leads']} | Warm: {summary['warm_leads']}")
        
        print(f"\n  💰 SALES")
        print(f"     Deals closed: {summary['deals_closed']}")
        print(f"     Total value: ${summary['total_deal_value']:,}")
        print(f"     Lead→Deal: {report['conversion_rates']['lead_to_deal']}%")
        
        print(f"\n  👥 CLIENTS")
        print(f"     Active: {summary['active_clients']}")
        print(f"     Total MRR: ${summary['total_mrr']:,}")
        
        if report['active_clients']:
            print(f"\n     Active Client Details:")
            for client in report['active_clients']:
                print(f"       • {client['company']}: ${client['mrr']}/mo — {client['time_saved']}/week saved")
        
        print(f"\n  📚 CASE STUDIES: {summary['case_studies']}")
        
        if report['recent_case_studies']:
            print(f"\n     Recent Wins:")
            for cs in report['recent_case_studies']:
                print(f"       • {cs['client']}: {cs['results']['time_saved']}/week")
        
        # Generate invoice requests
        if generate_invoices and data['clients']:
            invoices = self.generate_invoice_requests(data['clients'])
            
            if invoices:
                print(f"\n  🧾 INVOICE REQUESTS ({len(invoices)} pending)")
                print(f"  {'='*46}")
                
                for inv in invoices:
                    print(f"\n     Invoice: {inv['id']}")
                    print(f"     To: {inv['recipient']['contact_name']} @ {inv['recipient']['company']}")
                    print(f"     Amount: ${inv['total_due']:,}")
                    print(f"     Due: {inv['due_date']}")
                    print(f"     Notes: {inv['notes'][:60]}...")
                    
                    # Send Telegram notification
                    self.notifier.invoice_requested(inv)
                
                # Save invoice requests
                filepath = PIPELINE_DIR / "invoices.json"
                existing = []
                if filepath.exists():
                    with open(filepath) as f:
                        content = f.read().strip()
                        if content:
                            existing = json.loads(content)
                existing.extend(invoices)
                with open(filepath, 'w') as f:
                    json.dump(existing, f, indent=2)
                
                print(f"\n  💾 Invoice requests saved to pipeline/invoices.json")
                print(f"  ⚠️  ACTION REQUIRED: Send invoices manually")
        
        # Save report
        report_file = PIPELINE_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Send daily summary notification
        self.notifier.daily_summary(report)
        
        print(f"\n  💾 Report saved: {report_file.name}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--invoices', action='store_true', help='Generate invoice requests')
    args = parser.parse_args()
    
    agent = OpsAgent()
    agent.run(generate_invoices=args.invoices)


if __name__ == "__main__":
    main()
