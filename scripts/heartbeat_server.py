#!/usr/bin/env python3
"""
Nexus Automation — Status Endpoint
Exposes pipeline status for debugging.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

def get_pipeline_status():
    """Read pipeline state from files."""
    status = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_runs": [],
        "leads_total": 0,
        "leads_by_track": {},
        "last_run": None,
        "errors": []
    }
    
    try:
        # Find all lead files
        if PIPELINE_DIR.exists():
            lead_files = list(PIPELINE_DIR.glob("leads_*.json"))
            status["pipeline_runs"] = [f.name for f in lead_files]
            
            # Count total leads
            total_leads = 0
            for f in lead_files:
                try:
                    with open(f) as fp:
                        leads = json.load(fp)
                        total_leads += len(leads)
                        
                        # Count by track
                        for lead in leads:
                            track = lead.get('experiment_track', 'general')
                            status["leads_by_track"][track] = status["leads_by_track"].get(track, 0) + 1
                except:
                    pass
            
            status["leads_total"] = total_leads
            
            # Get last run time from most recent file
            if lead_files:
                latest = max(lead_files, key=lambda x: x.stat().st_mtime)
                status["last_run"] = datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
        
        # Check for error logs
        error_log = PIPELINE_DIR / "errors.log"
        if error_log.exists():
            with open(error_log) as f:
                status["errors"] = f.read().strip().split("\n")[-5:]  # Last 5 errors
                
    except Exception as e:
        status["errors"].append(str(e))
    
    return status

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok",
                "service": "nexus-automation",
                "timestamp": datetime.now().isoformat(),
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = get_pipeline_status()
            self.wfile.write(json.dumps(status, indent=2).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get quick stats
            stats = get_pipeline_status()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nexus Automation</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
                    h1 {{ color: #1a1a1a; }}
                    .status {{ padding: 15px; border-radius: 8px; margin: 20px 0; }}
                    .ok {{ background: #d4edda; color: #155724; }}
                    .stats {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                    .track {{ margin: 10px 0; padding: 10px; background: white; border-radius: 4px; }}
                    code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; }}
                </style>
            </head>
            <body>
                <h1>🤖 Nexus Automation</h1>
                <div class="status ok">
                    <strong>Status:</strong> Running<br>
                    <strong>Last Check:</strong> {stats['timestamp'][:19]}
                </div>
                
                <div class="stats">
                    <h2>Pipeline Stats</h2>
                    <p><strong>Total Leads:</strong> {stats['leads_total']}</p>
                    <p><strong>Last Run:</strong> {stats['last_run'][:19] if stats['last_run'] else 'Never'}</p>
                    <p><strong>Pipeline Runs:</strong> {len(stats['pipeline_runs'])}</p>
                    
                    <h3>Leads by Track</h3>
                    {''.join(f'<div class="track"><strong>{track}:</strong> {count} leads</div>' for track, count in stats['leads_by_track'].items()) or '<p>No leads yet</p>'}
                </div>
                
                <p><strong>Endpoints:</strong></p>
                <ul>
                    <li><code>/health</code> — Health check</li>
                    <li><code>/status</code> — Pipeline status (JSON)</li>
                </ul>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def run_server(port=8000):
    server = HTTPServer(('0.0.0.0', port), StatusHandler)
    print(f"Status server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    run_server(port)
