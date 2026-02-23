#!/usr/bin/env python3
"""
Nexus Automation — Lead Gen Agent
Scrapes job boards, Twitter, Reddit for operational pain signals.
LIVE MODE: Uses real Twitter API + mock job boards (Phase 1)
"""

import json
import os
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from experiments import ExperimentTracker
from job_boards import JobBoardScraper

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

def load_config():
    with open(SKILL_DIR / "references" / "config.json") as f:
        return json.load(f)

class LeadGenAgent:
    def __init__(self):
        self.config = load_config()
        self.experiments = ExperimentTracker()
        self.job_scraper = JobBoardScraper()
        self.pain_keywords = self.config['lead_gen']['pain_keywords']
        self.twitter_api_key = os.environ.get('TWITTER_API_KEY')
        self.live_mode = os.environ.get('NEXUS_MODE') == 'live'
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
        
    # ============ MOCK DATA SOURCES ============
    
    def mock_indeed_jobs(self) -> List[Dict]:
        """Mock Indeed job postings showing operational pain."""
        return [
            {
                "id": "indeed_001",
                "source": "indeed",
                "company": "RapidCart",
                "title": "Data Entry Specialist",
                "description": "Fast-growing e-commerce company seeking data entry specialist to manually update inventory across multiple platforms. 40+ hours/week copying data between Shopify, Amazon, and internal systems.",
                "location": "Remote",
                "posted": "2 days ago",
                "company_size": "25-50",
                "industry": "ecommerce"
            },
            {
                "id": "indeed_002", 
                "source": "indeed",
                "company": "CloudSync SaaS",
                "title": "Operations Associate",
                "description": "Join our team! Responsibilities include manual reconciliation of customer accounts, spreadsheet management, and data migration between tools. Attention to detail required.",
                "location": "Austin, TX",
                "posted": "1 day ago",
                "company_size": "50-100",
                "industry": "saas"
            },
            {
                "id": "indeed_003",
                "source": "indeed", 
                "company": "GrowthLabs Agency",
                "title": "Junior VA - Client Reporting",
                "description": "Looking for virtual assistant to compile weekly client reports. Involves copying data from 5+ platforms into PowerPoint decks. 20 hrs/week.",
                "location": "Remote",
                "posted": "3 days ago",
                "company_size": "10-25",
                "industry": "agency"
            }
        ]
    
    def mock_twitter_pain(self) -> List[Dict]:
        """Mock Twitter posts complaining about manual work."""
        return [
            {
                "id": "tw_001",
                "source": "twitter",
                "author": "marissa_founder",
                "author_name": "Marissa Chen",
                "bio": "Founder @RapidCart | 3x founder | E-commerce operator",
                "followers": 3400,
                "text": "Spending 4 hours every morning manually reconciling inventory across Shopify, Amazon, and our warehouse system. This is insane. There has to be a better way 😭",
                "posted": "5 hours ago"
            },
            {
                "id": "tw_002",
                "source": "twitter",
                "author": "david_cto",
                "author_name": "David Park",
                "bio": "CTO @CloudSync | Ex-Amazon | Building the future of data",
                "followers": 8900,
                "text": "Just approved hiring our 4th operations person for manual data reconciliation. Feels like we're treating the symptom not the disease. What are others doing for automated data pipelines?",
                "posted": "2 hours ago"
            },
            {
                "id": "tw_003",
                "source": "twitter",
                "author": "sarah_agency",
                "author_name": "Sarah Miller",
                "bio": "CEO @GrowthLabs | Helping brands scale | 50+ clients served",
                "followers": 2100,
                "text": "My team spends 30+ hours/week copying data between platforms for client reports. This is not sustainable. Looking for automation solutions — any recommendations?",
                "posted": "1 day ago"
            },
            {
                "id": "tw_004",
                "source": "twitter",
                "author": "random_dev",
                "author_name": "Alex Johnson",
                "bio": "Software engineer | Open source contributor",
                "followers": 340,
                "text": "Manual testing is boring, wish it was automated",
                "posted": "30 minutes ago"
            }
        ]
    
    def mock_reddit_pain(self) -> List[Dict]:
        """Mock Reddit posts from business subreddits."""
        return [
            {
                "id": "rd_001",
                "source": "reddit",
                "subreddit": "smallbusiness",
                "author": "shop_owner_2024",
                "title": "How do you handle inventory across multiple platforms?",
                "text": "I run a small e-commerce business doing about $50k/month. Currently selling on Shopify, Amazon, and Etsy. I'm spending 2-3 hours daily just updating inventory counts manually. It's killing me. What solutions have worked for you?",
                "upvotes": 45,
                "comments": 23,
                "posted": "1 day ago"
            },
            {
                "id": "rd_002",
                "source": "reddit",
                "subreddit": "operations",
                "author": "ops_manager_saas",
                "title": "Team of 5 spending 100+ hours/week on manual reporting",
                "text": "I'm head of ops at a 60-person SaaS company. Our client success team manually compiles reports from 6 different tools every week. It's 20 hours per person. Leadership won't approve more headcount but won't invest in automation either. How do I make the business case?",
                "upvotes": 127,
                "comments": 56,
                "posted": "2 days ago"
            }
        ]
    
    # ============ LIVE DATA SOURCES ============
    
    def search_twitter_by_track(self, track_id: str) -> List[Dict]:
        """Search Twitter for track-specific queries."""
        queries = self.experiments.get_queries_for_track(track_id)
        all_tweets = []
        
        if not self.twitter_api_key or not self.live_mode:
            print(f"  ⚠️  Twitter not configured, skipping {track_id}")
            return []
        
        for query in queries[:2]:  # Limit to save credits
            try:
                url = "https://api.twitter.com/2/tweets/search/recent"
                params = {
                    "query": query,
                    "max_results": 10,
                    "tweet.fields": "author_id,created_at,public_metrics"
                }
                headers = {"Authorization": f"Bearer {self.twitter_api_key}"}
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get("data", [])
                    
                    for tweet in tweets:
                        # Score against track
                        score, signals = self.experiments.score_lead_for_track(tweet["text"], track_id)
                        
                        if score >= 40:  # Minimum threshold
                            all_tweets.append({
                                "id": f"tw_{track_id}_{tweet['id']}",
                                "source": "twitter",
                                "track": track_id,
                                "author": tweet.get("author_id", "unknown"),
                                "author_name": "Twitter User",
                                "bio": "",
                                "followers": tweet.get("public_metrics", {}).get("impression_count", 0),
                                "text": tweet["text"],
                                "posted": tweet["created_at"],
                                "track_score": score,
                                "track_signals": signals
                            })
                    
                    print(f"  🐦 [{track_id}] '{query[:25]}...': {len(tweets)} tweets, {len([t for t in all_tweets if t.get('track') == track_id])} qualified")
                    
            except Exception as e:
                print(f"  ⚠️  Twitter search failed for {track_id}: {e}")
        
        return all_tweets
    
    def search_twitter_live(self) -> List[Dict]:
        """Search Twitter API for real pain signals."""
        if not self.twitter_api_key:
            print("  ⚠️  No TWITTER_API_KEY found, using mock data")
            return self.mock_twitter_pain()
        
        queries = [
            '"data entry" hiring',
            '"manual work" team',
            '"spreadsheet hell"',
            '"copying and pasting" work',
            '"hiring VA" OR "hiring assistant"',
        ]
        
        all_tweets = []
        
        for query in queries[:2]:  # Limit to 2 queries to save credits
            try:
                url = f"https://api.twitter.com/2/tweets/search/recent"
                params = {
                    "query": query,
                    "max_results": 10,
                    "tweet.fields": "author_id,created_at,public_metrics"
                }
                headers = {"Authorization": f"Bearer {self.twitter_api_key}"}
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get("data", [])
                    
                    for tweet in tweets:
                        all_tweets.append({
                            "id": f"tw_live_{tweet['id']}",
                            "source": "twitter",
                            "author": tweet.get("author_id", "unknown"),
                            "author_name": "Twitter User",  # Would need user lookup
                            "bio": "",
                            "followers": tweet.get("public_metrics", {}).get("impression_count", 0),
                            "text": tweet["text"],
                            "posted": tweet["created_at"]
                        })
                    
                    print(f"  🐦 Twitter query '{query[:30]}...': {len(tweets)} tweets")
                else:
                    print(f"  ⚠️  Twitter API error: {response.status_code}")
                    
            except Exception as e:
                print(f"  ⚠️  Twitter search failed: {e}")
        
        # If no live tweets, fall back to mock
        if not all_tweets:
            print("  ⚠️  No live tweets, using mock data")
            return self.mock_twitter_pain()
        
        return all_tweets
    
    # ============ SCORING ENGINE ============
    
    def score_pain(self, text: str) -> tuple[int, List[str]]:
        """Score pain intensity 0-100."""
        score = 0
        signals = []
        text_lower = text.lower()
        
        # Time quantified
        time_match = re.search(r'(\d+)\+?\s*(hours?|hrs?)', text_lower)
        if time_match:
            hours = int(time_match.group(1))
            if hours >= 20:
                score += 35
                signals.append(f"High time cost: {hours}+ hours")
            elif hours >= 5:
                score += 25
                signals.append(f"Moderate time cost: {hours} hours")
            else:
                score += 15
                signals.append(f"Time mentioned: {hours} hours")
        
        # Daily frequency
        if re.search(r'(every|each)\s+(day|morning|week)', text_lower):
            score += 20
            signals.append("Daily recurring pain")
        
        # Pain keywords (with stemming for variations)
        keyword_patterns = [
            ('data entry', ['data entry']),
            ('manual', ['manual', 'manually']),
            ('spreadsheet', ['spreadsheet', 'excel']),
            ('copy', ['copy', 'copying', 'paste', 'pasting']),
            ('reconciliation', ['reconciliation', 'reconciling']),
            ('inventory', ['inventory']),
            ('hiring', ['hiring', 'hire']),
        ]
        for category, patterns in keyword_patterns:
            if any(p in text_lower for p in patterns):
                score += 15
                signals.append(f"Keyword: {category}")
                break
        
        # Emotional intensity
        emotion_words = ['killing', 'insane', 'brutal', 'hell', 'nightmare', '😭', '🤬']
        if any(w in text_lower for w in emotion_words):
            score += 20
            signals.append("Emotional intensity high")
        
        # Hiring signal = budget confirmed
        if 'hiring' in text_lower or 'headcount' in text_lower:
            score += 25
            signals.append("Budget confirmed: hiring")
        
        return min(score, 100), list(set(signals))
    
    def score_authority(self, item: Dict) -> tuple[int, str]:
        """Score decision-making authority."""
        bio = item.get('bio', '').lower()
        title = item.get('title', '').lower()
        combined = bio + ' ' + title
        
        score = 0
        
        authority_tiers = [
            (['founder', 'ceo', 'owner', 'co-founder'], 45),
            (['cto', 'coo', 'chief'], 40),
            (['head of', 'vp ', 'vice president'], 30),
            (['director', 'manager'], 20),
        ]
        
        for keywords, points in authority_tiers:
            if any(kw in combined for kw in keywords):
                score += points
                break
        
        followers = item.get('followers', 0)
        if followers > 5000:
            score += 25
        elif followers > 1000:
            score += 15
        elif followers > 500:
            score += 10
        
        if score >= 60:
            tier = "decision_maker"
        elif score >= 35:
            tier = "influencer"
        else:
            tier = "individual"
        
        return min(score, 100), tier
    
    def detect_industry(self, item: Dict) -> str:
        """Detect industry from content."""
        combined = (item.get('text', '') + ' ' + item.get('description', '')).lower()
        
        indicators = [
            (['ecommerce', 'shopify', 'amazon', 'etsy', 'inventory', 'product'], 'ecommerce'),
            (['saas', 'software', 'api', 'platform', 'tech company'], 'saas'),
            (['agency', 'client', 'marketing', 'brand'], 'agency'),
            (['fintech', 'finance', 'reconciliation', 'payment', 'banking'], 'fintech'),
            (['consulting', 'advisor', 'services'], 'consulting'),
        ]
        
        for keywords, industry in indicators:
            if any(k in combined for k in keywords):
                return industry
        return 'other'
    
    def calculate_score(self, item: Dict) -> Optional[Dict]:
        """Calculate composite lead score."""
        text = item.get('text', '') + ' ' + item.get('description', '') + ' ' + item.get('title', '')
        
        pain_score, pain_signals = self.score_pain(text)
        if pain_score < 40:
            return None
        
        authority_score, authority_tier = self.score_authority(item)
        industry = self.detect_industry(item)
        
        # Industry multiplier
        multipliers = {'saas': 1.0, 'ecommerce': 1.0, 'agency': 0.95, 'fintech': 0.95, 'consulting': 0.9, 'other': 0.8}
        multiplier = multipliers.get(industry, 0.8)
        
        # Budget proxy (simplified)
        budget_score = 60
        if 'hiring' in text.lower():
            budget_score = 85
        elif item.get('company_size') in ['50-100', '100-200']:
            budget_score = 75
        elif item.get('company_size') in ['25-50']:
            budget_score = 65
        
        total = int((pain_score * 0.45 + authority_score * 0.30 + budget_score * 0.25) * multiplier)
        
        # Demo mode: lower threshold for demonstration
        min_score = 50  # Lowered from 75 for demo purposes
        if total < min_score:
            return None
        
        return {
            "id": f"nexus_{item['id']}",
            "discovered_at": datetime.now().isoformat(),
            "source": item['source'],
            "company": item.get('company', 'Unknown'),
            "contact": {
                "name": item.get('author_name', 'Unknown'),
                "handle": item.get('author', ''),
                "bio": item.get('bio', ''),
                "followers": item.get('followers', 0),
            },
            "pain": {
                "text": item.get('text', item.get('description', '')),
                "signals": pain_signals,
                "score": pain_score,
            },
            "authority": {
                "score": authority_score,
                "tier": authority_tier,
            },
            "context": {
                "industry": industry,
                "company_size": item.get('company_size', 'unknown'),
                "budget_score": budget_score,
            },
            "score": {
                "total": total,
                "tier": "hot" if total >= 85 else "warm" if total >= 75 else "cool",
            },
            "outreach": {
                "status": "pending",
                "hook": self._generate_hook(item, pain_signals, industry),
                "offer": self._recommend_offer(industry, text),
            }
        }
    
    def _generate_hook(self, item: Dict, signals: List[str], industry: str) -> str:
        """Generate personalized outreach hook."""
        name = item.get('author_name', 'there').split()[0]
        text = (item.get('text', '') + item.get('description', '')).lower()
        
        if 'inventory' in text:
            return f"Hey {name} — saw your post about inventory reconciliation eating your mornings. We built an automation that syncs inventory across platforms in real-time. Want to see it in action (free 2-week pilot)?"
        elif 'report' in text or 'client' in text:
            return f"Hi {name} — 30+ hours on client reports is brutal. We automated a similar workflow for an agency, cut it to 2 hours/week. Happy to build you a free proof-of-concept?"
        elif 'reconciliation' in text or 'data' in text:
            return f"Hey {name} — before you hire that next ops person, want to see if the reconciliation work can just... happen automatically? We'll build it free, you only pay if it works."
        else:
            return f"Hi {name} — saw your post about manual work. Nexus Automation specializes in eliminating repetitive operations. Worth a 10-min chat to explore?"
    
    def _recommend_offer(self, industry: str, text: str) -> str:
        """Recommend freemium offer."""
        text_lower = text.lower()
        
        if 'inventory' in text_lower:
            return "Multi-platform inventory sync (free 2-week pilot)"
        elif 'report' in text_lower:
            return "Client reporting automation (free dashboard + 1 month)"
        elif 'reconciliation' in text_lower:
            return "Automated reconciliation workflow (free setup + trial)"
        elif 'data entry' in text_lower:
            return "Data entry automation bot (free build + 100 tasks)"
        elif industry == 'agency':
            return "Client onboarding automation (free workflow + 30 days)"
        elif industry == 'saas':
            return "User provisioning automation (free integration + trial)"
        else:
            return "Custom workflow automation (free audit + pilot build)"
    
    # ============ MAIN EXECUTION ============
    
    def run(self, sources: List[str] = None) -> List[Dict]:
        """Run lead generation across all sources with experiment tracking."""
        if sources is None:
            sources = ['indeed', 'twitter', 'reddit']
        
        print("🔍 Nexus Automation — Lead Gen Agent")
        print(f"🧪 LIVE MODE: {self.live_mode}")
        print(f"🧪 TWITTER API: {'configured' if self.twitter_api_key else 'missing'}")
        print("=" * 50)
        
        all_raw = []
        
        # Run experiments: search each track on Twitter + Job Boards
        for track_id in self.experiments.experiments["experiments"]["active_tracks"]:
            track = self.experiments.experiments["tracks"].get(track_id, {})
            
            print(f"\n  📊 Track: {track.get('name', track_id)}")
            
            # Twitter search
            if 'twitter' in sources:
                track_tweets = self.search_twitter_by_track(track_id)
                all_raw.extend(track_tweets)
            
            # Job board search
            if 'indeed' in sources:
                job_queries = track.get('job_board_queries', [])
                if job_queries:
                    track_jobs = self.job_scraper.search_by_track(track_id, job_queries)
                    all_raw.extend(track_jobs)
        
        # Skip mock data in live mode
        if 'reddit' in sources and not self.live_mode:
            all_raw.extend(self.mock_reddit_pain())
            print(f"\n  👽 Loaded {len(self.mock_reddit_pain())} mock Reddit posts")
        elif 'reddit' in sources and self.live_mode:
            print(f"\n  👽 Reddit: Skipped (live mode)")
        
        print(f"\n  📊 Processing {len(all_raw)} raw signals...")
        
        leads = []
        for item in all_raw:
            lead = self.calculate_score(item)
            if lead:
                # Add track info if present
                if 'track' in item:
                    lead['experiment_track'] = item['track']
                    lead['track_score'] = item.get('track_score', 0)
                    self.experiments.log_lead(item['track'], lead)
                leads.append(lead)
        
        leads.sort(key=lambda x: x['score']['total'], reverse=True)
        
        # Save to pipeline
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = PIPELINE_DIR / f"leads_{timestamp}.json"
        with open(filepath, 'w') as f:
            json.dump(leads, f, indent=2)
        
        # Display results
        print(f"\n  ✅ Qualified {len(leads)} leads (min score: 50)")
        print(f"  💾 Saved to: {filepath}\n")
        
        hot = [l for l in leads if l['score']['tier'] == 'hot']
        warm = [l for l in leads if l['score']['tier'] == 'warm']
        
        print("  📋 TOP LEADS:")
        for lead in leads[:5]:
            tier = lead['score']['tier'].upper()
            score = lead['score']['total']
            name = lead['contact']['name']
            company = lead['company']
            track = lead.get('experiment_track', 'general')
            print(f"    [{tier}] [{track}] {name} @ {company} — Score: {score}")
            print(f"         Hook: {lead['outreach']['hook'][:60]}...")
        
        print(f"\n  📈 Summary: {len(hot)} HOT, {len(warm)} WARM leads ready")
        
        # Show experiment results
        print(f"\n  🧪 EXPERIMENT RESULTS:")
        summary = self.experiments.get_summary()
        for track_id, data in summary.items():
            print(f"    • {data['name']}: {data['total_leads']} leads, {data['high_quality']} high quality")
        
        # Save experiment results
        exp_file = self.experiments.save_results()
        print(f"\n  💾 Experiment results saved: {exp_file.name}")
        
        return leads


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', choices=['indeed', 'twitter', 'reddit', 'all'], default='all')
    args = parser.parse_args()
    
    sources = ['indeed', 'twitter', 'reddit'] if args.source == 'all' else [args.source]
    
    agent = LeadGenAgent()
    agent.run(sources)


if __name__ == "__main__":
    main()
