#!/usr/bin/env python3
"""
Nexus Automation — Sales Agent
Handles discovery calls, qualification, and closing.
Dry run mode: simulates conversations, outputs deals.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

def load_config():
    with open(SKILL_DIR / "references" / "config.json") as f:
        return json.load(f)

class SalesAgent:
    def __init__(self):
        self.config = load_config()
        self.questions = self.config['sales']['discovery_questions']
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_meetings(self) -> List[Dict]:
        """Load booked meetings from pipeline."""
        filepath = PIPELINE_DIR / "meetings.json"
        if not filepath.exists():
            return []
        
        with open(filepath) as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    
    def simulate_discovery_call(self, meeting: Dict) -> Dict:
        """Simulate a discovery call with prospect."""
        lead = meeting['lead']
        name = lead['contact']['name'].split()[0]
        company = lead['company']
        
        print(f"\n  📞 DISCOVERY CALL: {name} @ {company}")
        print("  " + "-" * 40)
        
        # Simulate Q&A
        discovery_notes = {}
        
        for q in self.questions:
            print(f"\n  🤖 Agent: {q}")
            
            # Generate realistic prospect answer based on their pain
            answer = self._generate_answer(lead, q)
            print(f"  👤 {name}: {answer}")
            
            discovery_notes[q] = answer
        
        # Qualification scoring
        qualification = self._qualify_opportunity(lead, discovery_notes)
        
        print(f"\n  📊 QUALIFICATION SCORE: {qualification['score']}/100")
        print(f"     Pain confirmed: {qualification['pain_confirmed']}")
        print(f"     Budget confirmed: {qualification['budget_confirmed']}")
        print(f"     Timeline: {qualification['timeline']}")
        print(f"     Decision maker: {qualification['decision_maker']}")
        
        # Close or nurture
        # Demo mode: lower qualification threshold
        if qualification['score'] >= 50:
            deal = self._close_deal(lead, discovery_notes, qualification)
            print(f"\n  ✅ DEAL CLOSED: ${deal['value']}/month")
            return {"outcome": "closed_won", "deal": deal}
        else:
            print(f"\n  ❌ NOT QUALIFIED — Added to nurture")
            return {"outcome": "nurture", "notes": discovery_notes}
    
    def _generate_answer(self, lead: Dict, question: str) -> str:
        """Generate realistic prospect answers."""
        pain_text = lead.get('pain', {}).get('text', '').lower()
        industry = lead.get('context', {}).get('industry', 'other')
        
        answers = {
            "What manual work takes up most of your team's time?": [
                f"Honestly? Copying data between our CRM and billing system. Takes 2-3 hours daily.",
                f"Inventory reconciliation across Shopify, Amazon, and our warehouse. It's a nightmare.",
                f"Client reporting. We pull data from 5 platforms to build weekly decks. 20+ hours/week.",
            ],
            "How many hours per week are spent on repetitive tasks?": [
                f"I'd estimate 30-40 hours across the team. Maybe more.",
                f"At least 25 hours. Probably higher if we tracked it properly.",
                f"Easily 50+ hours. It's basically a full-time person's job.",
            ],
            "What happens if this work doesn't get done?": [
                f"Clients don't get billed on time. Cash flow nightmare.",
                f"We oversell inventory. Then we have to cancel orders. Customer service hell.",
                f"Clients churn. They expect these reports weekly. No report = no renewal.",
            ],
            "Have you tried automation before? What happened?": [
                f"We tried Zapier but hit limits. Couldn't handle the complexity.",
                f"Hired a dev to build something. It broke after 3 months. He left.",
                f"Looked at some tools but couldn't justify the cost without proof it would work.",
            ],
            "What's the cost of continuing manually?": [
                f"We're hiring a 3rd person for this next quarter. That's $60k+ annually.",
                f"Opportunity cost is huge. My ops lead should be on strategy, not copy-paste.",
                f"Hard to quantify, but we lose at least one client/month to competitors with better reporting.",
            ],
        }
        
        return random.choice(answers.get(question, ["It's complicated."]))
    
    def _qualify_opportunity(self, lead: Dict, notes: Dict) -> Dict:
        """Score qualification based on discovery."""
        score = 0
        
        # Pain confirmed (0-30)
        pain_keywords = ['hours', 'nightmare', 'hell', 'daily', 'weekly', 'copying', 'manual']
        pain_mentions = sum(1 for note in notes.values() if any(kw in note.lower() for kw in pain_keywords))
        pain_score = min(pain_mentions * 10, 30)
        score += pain_score
        
        # Budget confirmed (0-25)
        budget_keywords = ['hiring', '60k', 'cost', 'expensive', 'person']
        budget_mentions = sum(1 for note in notes.values() if any(kw in note.lower() for kw in budget_keywords))
        budget_score = min(budget_mentions * 12, 25)
        score += budget_score
        
        # Timeline (0-25)
        timeline_score = 20 if 'next quarter' in str(notes) or 'monthly' in str(notes) else 15
        score += timeline_score
        
        # Decision maker (0-20)
        dm_score = 20 if lead.get('authority', {}).get('tier') == 'decision_maker' else 10
        score += dm_score
        
        return {
            "score": score,
            "pain_confirmed": pain_score >= 20,
            "budget_confirmed": budget_score >= 12,
            "timeline": "within_30_days" if timeline_score >= 20 else "future",
            "decision_maker": dm_score >= 20,
        }
    
    def _close_deal(self, lead: Dict, notes: Dict, qualification: Dict) -> Dict:
        """Determine deal terms and close."""
        # Determine tier based on pain/budget signals
        budget_signals = str(notes).lower()
        
        if '60k' in budget_signals or '3rd person' in budget_signals or 'hiring' in budget_signals:
            tier = 'growth'
            value = 2000
        elif '50+ hours' in budget_signals or 'full-time' in budget_signals:
            tier = 'growth'
            value = 2000
        elif '30-40' in budget_signals or '25 hours' in budget_signals:
            tier = 'starter'
            value = 500
        else:
            tier = 'starter'
            value = 500
        
        # Override for enterprise signals
        if lead.get('context', {}).get('company_size') in ['100-200', '200+']:
            tier = 'enterprise'
            value = 5000
        
        return {
            "id": f"deal_{lead['id']}",
            "lead_id": lead['id'],
            "company": lead['company'],
            "contact": lead['contact'],
            "tier": tier,
            "value": value,
            "billing": "monthly",
            "pilot_duration_days": 14,
            "status": "closed_won",
            "closed_at": datetime.now().isoformat(),
            "discovery_notes": notes,
            "qualification": qualification,
        }
    
    def run(self):
        """Run sales process on booked meetings."""
        print("🎯 Nexus Automation — Sales Agent")
        print("=" * 50)
        
        meetings = self.load_meetings()
        
        if not meetings:
            print("  ⚠️  No meetings booked. Run outreach first.")
            return
        
        print(f"  📅 Processing {len(meetings)} discovery calls\n")
        
        deals = []
        nurtures = []
        
        for meeting in meetings:
            result = self.simulate_discovery_call(meeting)
            
            if result['outcome'] == 'closed_won':
                deals.append(result['deal'])
            else:
                nurtures.append({
                    "lead_id": meeting['lead']['id'],
                    "notes": result['notes']
                })
        
        # Save deals
        if deals:
            self._save_deals(deals)
            print(f"\n  💰 DEALS SAVED: {len(deals)} closed")
            total_value = sum(d['value'] for d in deals)
            print(f"     Total MRR potential: ${total_value:,}/month")
        
        if nurtures:
            print(f"  📋 NURTURED: {len(nurtures)} leads for future")
        
        # Clear processed meetings
        meetings_file = PIPELINE_DIR / "meetings.json"
        if meetings_file.exists():
            meetings_file.unlink()
        
        return deals
    
    def _save_deals(self, deals: List[Dict]):
        """Save closed deals to pipeline."""
        filepath = PIPELINE_DIR / "deals.json"
        existing = []
        if filepath.exists():
            with open(filepath) as f:
                content = f.read().strip()
                if content:
                    existing = json.loads(content)
        existing.extend(deals)
        with open(filepath, 'w') as f:
            json.dump(existing, f, indent=2)


def main():
    agent = SalesAgent()
    agent.run()


if __name__ == "__main__":
    main()
