#!/usr/bin/env python3
"""
Nexus Automation — Experiment Runner
Runs 3 niche tracks in parallel, tracks performance.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

def load_experiments():
    with open(SKILL_DIR / "references" / "experiments.json") as f:
        return json.load(f)

class ExperimentTracker:
    def __init__(self):
        self.experiments = load_experiments()
        self.results = {track: {"leads": [], "replies": 0, "meetings": 0, "deals": 0} 
                       for track in self.experiments["experiments"]["active_tracks"]}
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_queries_for_track(self, track_id: str) -> List[str]:
        """Get Twitter queries for a specific track."""
        track = self.experiments["tracks"].get(track_id, {})
        return track.get("twitter_queries", [])
    
    def get_offer_for_track(self, track_id: str) -> str:
        """Get offer text for a specific track."""
        track = self.experiments["tracks"].get(track_id, {})
        return track.get("offer", "Custom automation solution")
    
    def score_lead_for_track(self, text: str, track_id: str) -> tuple[int, List[str]]:
        """Score a lead against track-specific keywords."""
        track = self.experiments["tracks"].get(track_id, {})
        keywords = track.get("pain_keywords", [])
        
        score = 0
        signals = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                score += 20
                signals.append(keyword)
        
        # Boost for high-intent phrases
        intent_phrases = {
            "hiring": 25,  # Strong budget signal
            "looking for": 15,
            "need help": 15,
            "any recommendations": 10,
            "overwhelmed": 20,  # Pain intensity
            "drowning": 20,
            "nightmare": 20,
        }
        for phrase, points in intent_phrases.items():
            if phrase in text_lower:
                score += points
                signals.append(f"intent: {phrase}")
        
        return min(score, 100), list(set(signals))
    
    def generate_hook_for_track(self, name: str, text: str, track_id: str) -> str:
        """Generate track-specific outreach hook."""
        track = self.experiments["tracks"].get(track_id, {})
        offer = track.get("offer", "")
        
        hooks = {
            "customer_support": f"Hey {name} — saw your post about support challenges. {offer}. Free 2-week pilot to prove ROI?",
            "ecommerce_ops": f"Hi {name} — {offer.lower()}. We eliminate manual inventory work. Worth a 10-min chat?",
            "sales_automation": f"Hey {name} — {offer.lower()}. Free pilot: we build it, you only pay if it books meetings.",
        }
        
        return hooks.get(track_id, f"Hi {name} — {offer}")
    
    def log_lead(self, track_id: str, lead: Dict):
        """Log a lead for a track."""
        self.results[track_id]["leads"].append(lead)
    
    def get_summary(self) -> Dict:
        """Get experiment summary."""
        summary = {}
        for track_id, data in self.results.items():
            track_name = self.experiments["tracks"].get(track_id, {}).get("name", track_id)
            leads = data["leads"]
            
            summary[track_id] = {
                "name": track_name,
                "total_leads": len(leads),
                "high_quality": len([l for l in leads if l.get("score", 0) >= 75]),
                "avg_score": sum(l.get("score", 0) for l in leads) / len(leads) if leads else 0,
            }
        
        return summary
    
    def save_results(self):
        """Save experiment results."""
        filepath = PIPELINE_DIR / f"experiment_results_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filepath, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results,
                "summary": self.get_summary()
            }, f, indent=2)
        return filepath

if __name__ == "__main__":
    tracker = ExperimentTracker()
    
    print("🧪 Nexus Automation — Experiment Framework")
    print("=" * 50)
    
    for track_id in tracker.experiments["experiments"]["active_tracks"]:
        track = tracker.experiments["tracks"].get(track_id, {})
        print(f"\n📊 Track: {track.get('name', track_id)}")
        print(f"   Queries: {len(track.get('twitter_queries', []))}")
        print(f"   Offer: {track.get('offer', 'N/A')[:50]}...")
    
    print(f"\n✅ Experiment framework ready")
    print(f"   Duration: {tracker.experiments['experiments']['duration_days']} days")
    print(f"   Tracks: {len(tracker.experiments['experiments']['active_tracks'])}")
