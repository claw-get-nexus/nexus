#!/usr/bin/env python3
"""
Nexus Automation — Lead Gen Agent (HARDCODED 4 TRACKS)
Scrapes Twitter for operational pain signals across 4 niches.
"""

import json
import os
import re
import requests

# FORCE REDEPLOY: whitespace change

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

def load_config():
    with open(SKILL_DIR / "references" / "config.json") as f:
        return json.load(f)

class LeadGenAgent:
    def __init__(self):
        self.config = load_config()
        self.twitter_api_key = os.environ.get('TWITTER_API_KEY')
        self.live_mode = os.environ.get('NEXUS_MODE') == 'live'
        
        # HARDCODED 4 TRACKS
        self.tracks = {
            "customer_support": {
                "name": "Customer Support Automation",
                "queries": [
                    "support backlog team",
                    "hiring support agents",
                    "Zendesk alternative",
                    "overwhelmed tickets",
                    "customer service automation"
                ],
                "keywords": ["support tickets", "customer service", "help desk", "response time"]
            },
            "ecommerce_ops": {
                "name": "E-commerce Operations",
                "queries": [
                    "inventory sync Shopify Amazon",
                    "order processing manual",
                    "multi-channel inventory",
                    "ecommerce automation"
                ],
                "keywords": ["inventory", "order fulfillment", "multi-channel", "stock sync"]
            },
            "sales_automation": {
                "name": "Sales & RevOps Automation",
                "queries": [
                    "CRM cleanup",
                    "lead scoring",
                    "sales follow up",
                    "pipeline management"
                ],
                "keywords": ["CRM", "lead qualification", "follow up", "pipeline"]
            },
            "trade_business": {
                "name": "Trade Business Automation",
                "queries": [
                    "plumber overwhelmed jobs",
                    "electrician business admin",
                    "contractor scheduling",
                    "tradesman paperwork"
                ],
                "keywords": ["scheduling", "invoicing", "job tracking", "paperwork"]
            }
        }
        
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    
    def search_twitter(self, track_id: str, track_config: dict) -> List[Dict]:
        """Search Twitter for a specific track."""
        queries = track_config["queries"]
        all_tweets = []
        
        if not self.twitter_api_key:
            print(f"    ⚠️  No Twitter API key")
            return []
        
        for query in queries[:2]:
            try:
                url = "https://api.twitter.com/2/tweets/search/recent"
                params = {"query": query, "max_results": 10, "tweet.fields": "author_id,created_at,public_metrics"}
                headers = {"Authorization": f"Bearer {self.twitter_api_key}"}
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    tweets = response.json().get("data", [])
                    
                    for tweet in tweets:
                        text = tweet["text"]
                        # Simple scoring
                        score = 0
                        for kw in track_config["keywords"]:
                            if kw in text.lower():
                                score += 20
                        if "hiring" in text.lower():
                            score += 25
                        if "overwhelmed" in text.lower() or "drowning" in text.lower():
                            score += 20
                        
                        if score >= 40:
                            all_tweets.append({
                                "id": f"{track_id}_{tweet['id']}",
                                "source": "twitter",
                                "track": track_id,
                                "track_name": track_config["name"],
                                "author": tweet.get("author_id", "unknown"),
                                "author_name": "Twitter User",
                                "text": text,
                                "posted": tweet["created_at"],
                                "track_score": score
                            })
                    
                    print(f"    ✅ '{query[:25]}...': {len(tweets)} tweets, {len([t for t in all_tweets if t['track'] == track_id])} qualified")
                else:
                    print(f"    ⚠️  Twitter error {response.status_code}")
                    
            except Exception as e:
                print(f"    ⚠️  Search failed: {e}")
        
        return all_tweets
    
    def score_lead(self, item: Dict) -> Optional[Dict]:
        """Score and format a lead."""
        text = item.get("text", "")
        track = item.get("track", "general")
        track_name = item.get("track_name", "General")
        
        # Simple scoring
        pain_score = item.get("track_score", 50)
        
        # Authority (simplified)
        authority_score = 50
        
        # Budget
        budget_score = 70 if "hiring" in text.lower() else 50
        
        total = int(pain_score * 0.5 + authority_score * 0.25 + budget_score * 0.25)
        
        if total < 50:
            return None
        
        return {
            "id": item["id"],
            "discovered_at": datetime.now().isoformat(),
            "source": item["source"],
            "experiment_track": track,
            "track_name": track_name,
            "contact": {
                "name": "Twitter User",
                "handle": item["author"],
            },
            "pain": {"text": text, "score": pain_score},
            "score": {
                "total": total,
                "tier": "hot" if total >= 75 else "warm" if total >= 60 else "cool"
            },
            "outreach": {
                "status": "pending",
                "hook": f"Hi — saw your post about operational challenges. We build automation for {track_name.lower()}. Free 2-week pilot?"
            }
        }
    
    def run(self) -> List[Dict]:
        """Run lead generation for all 4 tracks."""
        print("🔍 Nexus Automation — Lead Gen Agent")
        print(f"🧪 LIVE MODE: {self.live_mode}")
        print("🧪 4 TRACKS: Support, E-commerce, Sales, Trade Business")
        print("=" * 60)
        
        all_raw = []
        
        # Search all tracks
        for track_id, track_config in self.tracks.items():
            print(f"\n  📊 {track_config['name']}")
            tweets = self.search_twitter(track_id, track_config)
            all_raw.extend(tweets)
        
        print(f"\n  📊 Processing {len(all_raw)} signals...")
        
        # Score leads
        leads = []
        track_counts = {}
        
        for item in all_raw:
            lead = self.score_lead(item)
            if lead:
                leads.append(lead)
                track = lead.get("experiment_track", "general")
                track_counts[track] = track_counts.get(track, 0) + 1
        
        leads.sort(key=lambda x: x["score"]["total"], reverse=True)
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = PIPELINE_DIR / f"leads_{timestamp}.json"
        with open(filepath, 'w') as f:
            json.dump(leads, f, indent=2)
        
        # Display
        print(f"\n  ✅ Qualified {len(leads)} leads (min score: 50)")
        print(f"  💾 Saved to: {filepath}")
        
        print(f"\n  📊 BY TRACK:")
        for track, count in track_counts.items():
            print(f"    • {track}: {count} leads")
        
        if leads:
            print(f"\n  📋 TOP LEAD:")
            lead = leads[0]
            print(f"    [{lead['score']['tier'].upper()}] {lead['track_name']}")
            print(f"    Score: {lead['score']['total']}")
            print(f"    Text: {lead['pain']['text'][:60]}...")
        
        return leads


if __name__ == "__main__":
    agent = LeadGenAgent()
    agent.run()
