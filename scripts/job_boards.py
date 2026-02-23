#!/usr/bin/env python3
"""
Nexus Automation — Job Board Scraper
Scrapes Indeed, Greenhouse, Lever for hiring signals.
"""

import json
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

SKILL_DIR = Path(__file__).parent.parent

class JobBoardScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_indeed(self, query: str, location: str = "") -> List[Dict]:
        """Search Indeed for job postings."""
        jobs = []
        
        try:
            # Indeed RSS feed (more stable than HTML scraping)
            url = f"https://rss.indeed.com/rss"
            params = {
                "q": query,
                "l": location,
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Parse RSS XML
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                # RSS namespace
                ns = {'ns': 'http://purl.org/rss/1.0/'}
                
                for item in root.findall('.//item'):
                    title = item.find('title')
                    description = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title is not None:
                        title_text = title.text or ""
                        # Extract company from title (format: "Job Title - Company")
                        company = "Unknown"
                        if " - " in title_text:
                            parts = title_text.rsplit(" - ", 1)
                            if len(parts) == 2:
                                title_text = parts[0]
                                company = parts[1]
                        
                        jobs.append({
                            "id": f"indeed_{hash(title_text + company) % 100000}",
                            "source": "indeed",
                            "company": company,
                            "title": title_text,
                            "description": description.text if description is not None else "",
                            "posted": pub_date.text if pub_date is not None else "recent",
                            "location": location or "Various",
                            "company_size": "unknown",
                            "industry": "unknown"
                        })
                
                print(f"  📋 Indeed '{query[:30]}...': {len(jobs)} jobs")
                
        except Exception as e:
            print(f"  ⚠️  Indeed search failed: {e}")
        
        return jobs
    
    def search_greenhouse(self, company: str = "") -> List[Dict]:
        """Search Greenhouse job board."""
        # Greenhouse requires specific company boards
        # This would need a list of target companies
        return []
    
    def search_by_track(self, track_id: str, queries: List[str]) -> List[Dict]:
        """Search job boards for track-specific roles."""
        all_jobs = []
        
        for query in queries[:3]:  # Limit to save time
            jobs = self.search_indeed(query)
            
            # Tag with track
            for job in jobs:
                job['track'] = track_id
            
            all_jobs.extend(jobs)
        
        return all_jobs

if __name__ == "__main__":
    scraper = JobBoardScraper()
    
    # Test search
    jobs = scraper.search_indeed("data entry")
    print(f"Found {len(jobs)} jobs")
    
    for job in jobs[:3]:
        print(f"  - {job['title']} @ {job['company']}")
