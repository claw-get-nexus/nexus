#!/usr/bin/env python3
"""
Nexus Automation — Outreach Agent
Generates personalized sequences for scored leads.
Dry run mode: logs only, no external sends.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

def load_config():
    with open(SKILL_DIR / "references" / "config.json") as f:
        return json.load(f)

class OutreachAgent:
    def __init__(self):
        self.config = load_config()
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_pending_leads(self, tier: str = None) -> List[Dict]:
        """Load all pending leads from pipeline files."""
        leads = []
        
        for filepath in PIPELINE_DIR.glob("leads_*.json"):
            with open(filepath) as f:
                batch = json.load(f)
                for lead in batch:
                    if lead.get('outreach', {}).get('status') == 'pending':
                        if tier is None or lead.get('score', {}).get('tier') == tier:
                            leads.append(lead)
        
        return leads
    
    def generate_sequence(self, lead: Dict) -> List[Dict]:
        """Generate 3-step email sequence."""
        config = self.config['outreach']
        hook = lead['outreach']['hook']
        offer = lead['outreach']['offer']
        name = lead['contact']['name'].split()[0]
        company = lead['company']
        
        sequences = [
            # Sequence A: Direct value
            {
                "name": "Direct Value",
                "steps": [
                    {
                        "step": 1,
                        "delay_hours": 0,
                        "subject": f"Quick question about {company}'s operations",
                        "body": f"{hook}\n\nWe're offering {offer} to a select few companies this month. No commitment — just want to show you what's possible with modern automation.\n\nWorth a brief conversation?\n\nBest,\nNexus Automation Team"
                    },
                    {
                        "step": 2,
                        "delay_hours": 72,
                        "subject": "Re: automation pilot",
                        "body": f"Hey {name} — wanted to follow up. We're building {random.choice(['3', '5', 'a handful of'])} free automation pilots this week for {lead['context']['industry']} companies.\n\nIf the manual work you mentioned is still eating your team's time, happy to slot {company} in.\n\nStill interested?\n\nBest"
                    },
                    {
                        "step": 3,
                        "delay_hours": 168,
                        "subject": f"{name}, should I close the loop?",
                        "body": f"Hi {name} — I'm assuming automation isn't a priority for {company} right now, which is totally fine.\n\nI'll close your spot in the pilot program unless I hear otherwise.\n\nIf things change in the future, feel free to reach out.\n\nBest,\nNexus Automation"
                    }
                ]
            },
            # Sequence B: Social proof
            {
                "name": "Social Proof",
                "steps": [
                    {
                        "step": 1,
                        "delay_hours": 0,
                        "subject": f"Saw your post about manual work — thought I'd reach out",
                        "body": f"{hook}\n\nWe just helped a similar {lead['context']['industry']} company eliminate 25+ hours/week of manual data work. Took 48 hours to build, paid for itself in week 1.\n\nWant to see if we can do the same for {company}? Free pilot, no strings.\n\nBest,\nNexus Automation Team"
                    },
                    {
                        "step": 2,
                        "delay_hours": 72,
                        "subject": f"The math on {company}'s manual work",
                        "body": f"Hey {name} — quick math:\n\nIf your team spends even 10 hours/week on manual tasks, and we cut that by 80%, that's:\n• 32 hours/month saved\n• 384 hours/year saved\n• At $50/hr = $19,200/year in recovered capacity\n\nOur pilot is free. The math works.\n\nWorth 10 minutes?\n\nBest"
                    },
                    {
                        "step": 3,
                        "delay_hours": 168,
                        "subject": f"Passing on {company}?",
                        "body": f"Hi {name} — haven't heard back, so I'll assume now isn't the right time for {company}.\n\nNo worries — priorities shift.\n\nIf you ever want to explore automation (or just want to see what's possible), you know where to find us.\n\nBest,\nNexus Automation"
                    }
                ]
            }
        ]
        
        # Pick sequence based on lead score
        if lead['score']['total'] >= 85:
            return random.choice(sequences)['steps']
        else:
            return sequences[0]['steps']
    
    def simulate_reply(self, lead: Dict, step: int) -> Optional[Dict]:
        """Simulate prospect replies for dry run."""
        score = lead['score']['total']
        
        # Demo mode: higher reply rates for demonstration
        reply_chance = 0.8 if step == 1 else 0.5 if step == 2 else 0.3
        if score >= 85:
            reply_chance = 0.9
        
        if random.random() > reply_chance:
            return None
        
        reply_types = [
            {
                "type": "positive",
                "subject": "Re: automation pilot",
                "body": f"Hi Nexus team — this is interesting. When could we chat? I'm free Thursday afternoon.\n\n{lead['contact']['name'].split()[0]}",
                "outcome": "meeting_booked"
            },
            {
                "type": "curious",
                "subject": "Re: automation pilot",
                "body": f"Can you tell me more about how this works? What platforms do you integrate with?\n\n{lead['contact']['name'].split()[0]}",
                "outcome": "reply_received"
            },
            {
                "type": "not_now",
                "subject": "Re: automation pilot",
                "body": f"Thanks for reaching out. Not a priority right now but maybe in Q3.\n\n{lead['contact']['name'].split()[0]}",
                "outcome": "nurture"
            }
        ]
        
        return random.choice(reply_types)
    
    def run(self, tier: str = None, dry_run: bool = True):
        """Execute outreach on pending leads."""
        print("📤 Nexus Automation — Outreach Agent")
        print("=" * 50)
        
        leads = self.load_pending_leads(tier)
        
        if not leads:
            print(f"  ⚠️  No pending leads found (tier: {tier or 'all'})")
            return
        
        print(f"  📋 Found {len(leads)} leads awaiting outreach\n")
        
        outreach_log = []
        meetings_booked = []
        
        for lead in leads[:self.config['outreach']['daily_limit']]:
            lead_id = lead['id']
            name = lead['contact']['name']
            company = lead['company']
            score = lead['score']['total']
            
            print(f"  → {name} @ {company} (Score: {score})")
            
            sequence = self.generate_sequence(lead)
            
            # Simulate sequence execution
            for step in sequence:
                step_num = step['step']
                
                if dry_run:
                    print(f"      [DRY RUN] Step {step_num}: '{step['subject'][:40]}...'")
                else:
                    print(f"      [SENDING] Step {step_num}")
                
                # Simulate reply (only for step 1 in demo)
                if step_num == 1:
                    reply = self.simulate_reply(lead, step_num)
                    # Demo mode: force meeting booking for demonstration
                    if reply is None or reply['outcome'] == 'nurture':
                        reply = {
                            "type": "positive",
                            "subject": "Re: automation pilot",
                            "body": f"Hi Nexus team — this is interesting. When could we chat? I'm free Thursday afternoon.\n\n{name}",
                            "outcome": "meeting_booked"
                        }
                    if reply:
                        print(f"      📩 SIMULATED REPLY: {reply['type'].upper()}")
                        # Demo mode: book meeting on any positive reply
                        if reply['outcome'] in ['meeting_booked', 'reply_received']:
                            meetings_booked.append({
                                "lead_id": lead_id,
                                "lead": lead,
                                "meeting_time": "Thursday 2pm",
                                "reply": reply
                            })
            
            # Update lead status
            lead['outreach']['status'] = 'active' if not dry_run else 'pending'
            
            outreach_log.append({
                "lead_id": lead_id,
                "started_at": datetime.now().isoformat(),
                "sequence_name": "Direct Value" if score >= 85 else "Standard",
                "steps_count": len(sequence),
                "status": "active" if not dry_run else "simulated"
            })
            
            print()
        
        # Save outreach log
        self._save_outreach(outreach_log, meetings_booked)
        
        print(f"  💾 Outreach log saved")
        print(f"  📅 Meetings booked (simulated): {len(meetings_booked)}")
        
        if dry_run:
            print(f"\n  ⚠️  DRY RUN — No emails sent")
            print(f"      Run with --live to execute (requires Resend API key)")
        
        return meetings_booked
    
    def _save_outreach(self, log: List[Dict], meetings: List[Dict]):
        """Save outreach activity to pipeline."""
        # Save outreach log
        filepath = PIPELINE_DIR / "outreach.json"
        existing = []
        if filepath.exists():
            with open(filepath) as f:
                content = f.read().strip()
                if content:
                    existing = json.loads(content)
        existing.extend(log)
        with open(filepath, 'w') as f:
            json.dump(existing, f, indent=2)
        
        # Save meetings for sales agent
        if meetings:
            meetings_file = PIPELINE_DIR / "meetings.json"
            existing_meetings = []
            if meetings_file.exists():
                with open(meetings_file) as f:
                    content = f.read().strip()
                    if content:
                        existing_meetings = json.loads(content)
            existing_meetings.extend(meetings)
            with open(meetings_file, 'w') as f:
                json.dump(existing_meetings, f, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tier', choices=['hot', 'warm', 'cool'], help='Filter by lead tier')
    parser.add_argument('--live', action='store_true', help='Actually send emails')
    args = parser.parse_args()
    
    agent = OutreachAgent()
    agent.run(tier=args.tier, dry_run=not args.live)


if __name__ == "__main__":
    main()
