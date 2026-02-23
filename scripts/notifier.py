#!/usr/bin/env python3
"""
Nexus Automation — Notification Module
Sends alerts via Telegram for business events.
"""

import json
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

class Notifier:
    def __init__(self):
        with open(SKILL_DIR / "references" / "config.json") as f:
            self.config = json.load(f)
        self.enabled = self.config.get('notifications', {}).get('channel') == 'telegram'
        self.events = self.config.get('notifications', {}).get('events', [])
    
    def send(self, event_type: str, message: str, data: dict = None):
        """Send notification if event type is enabled."""
        if not self.enabled:
            return
        
        if event_type not in self.events:
            return
        
        # Format message
        header = f"🔔 **Nexus Automation — {event_type.replace('_', ' ').title()}**"
        full_message = f"{header}\n\n{message}"
        
        if data:
            full_message += f"\n\n```json\n{json.dumps(data, indent=2)}\n```"
        
        # In dry run mode, just print to console
        # In live mode, this would call the Telegram API
        print(f"\n{'='*50}")
        print("TELEGRAM NOTIFICATION (simulated)")
        print(f"{'='*50}")
        print(full_message)
        print(f"{'='*50}\n")
        
        return full_message
    
    def hot_lead(self, lead: dict):
        """Notify about new hot lead."""
        name = lead.get('contact', {}).get('name', 'Unknown')
        company = lead.get('company', 'Unknown')
        score = lead.get('score', {}).get('total', 0)
        
        message = f"🎯 **Hot Lead Discovered**\n\n"
        message += f"**{name}** @ {company}\n"
        message += f"Score: {score}/100\n\n"
        message += f"Pain: {lead.get('pain', {}).get('text', 'N/A')[:100]}...\n\n"
        message += f"Hook ready: ✅\n"
        message += f"Action: Outreach queued"
        
        return self.send('hot_lead_discovered', message, {'lead_id': lead.get('id')})
    
    def meeting_booked(self, meeting: dict):
        """Notify about booked meeting."""
        lead = meeting.get('lead', {})
        name = lead.get('contact', {}).get('name', 'Unknown')
        company = lead.get('company', 'Unknown')
        
        message = f"📅 **Meeting Booked**\n\n"
        message += f"**{name}** @ {company}\n"
        message += f"Time: {meeting.get('meeting_time', 'TBD')}\n\n"
        message += f"Discovery call ready: ✅\n"
        message += f"Action: Sales agent will process"
        
        return self.send('meeting_booked', message)
    
    def deal_closed(self, deal: dict):
        """Notify about closed deal."""
        message = f"💰 **Deal Closed**\n\n"
        message += f"**{deal.get('company', 'Unknown')}**\n"
        message += f"Tier: {deal.get('tier', 'unknown').title()}\n"
        message += f"Value: ${deal.get('value', 0):,}/month\n\n"
        message += f"MRR added: +${deal.get('value', 0):,}/mo\n"
        message += f"Action: Fulfillment starting"
        
        return self.send('deal_closed', message, {'deal_id': deal.get('id')})
    
    def invoice_requested(self, invoice: dict):
        """Notify about invoice needing manual send."""
        message = f"🧾 **Invoice Requested**\n\n"
        message += f"**{invoice.get('recipient', {}).get('company', 'Unknown')}**\n"
        message += f"Amount: ${invoice.get('total_due', 0):,}\n"
        message += f"Due: {invoice.get('due_date', 'N/A')}\n\n"
        message += f"⚠️ **ACTION REQUIRED**\n"
        message += f"Send invoice manually via your billing system"
        
        return self.send('invoice_requested', message, {'invoice_id': invoice.get('id')})
    
    def daily_summary(self, report: dict):
        """Send daily business summary."""
        summary = report.get('summary', {})
        
        message = f"📊 **Daily Summary — {datetime.now().strftime('%Y-%m-%d')}**\n\n"
        message += f"📥 Leads: {summary.get('total_leads', 0)} (Hot: {summary.get('hot_leads', 0)})\n"
        message += f"💰 Deals: {summary.get('deals_closed', 0)} closed\n"
        message += f"👥 Clients: {summary.get('active_clients', 0)} active\n"
        message += f"📈 MRR: ${summary.get('total_mrr', 0):,}/month\n\n"
        
        if summary.get('total_mrr', 0) > 0:
            message += "✅ Business is running"
        else:
            message += "⏳ Awaiting first client"
        
        return self.send('daily_summary', message)


if __name__ == "__main__":
    # Test notifications
    notifier = Notifier()
    
    test_lead = {
        'id': 'test_001',
        'contact': {'name': 'Test User'},
        'company': 'TestCo',
        'score': {'total': 88},
        'pain': {'text': 'Spending 5 hours daily on manual data entry'}
    }
    
    notifier.hot_lead(test_lead)
