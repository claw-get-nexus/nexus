#!/usr/bin/env python3
"""
Nexus Automation — Debug Endpoint
Exposes pipeline logs for remote debugging.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

SKILL_DIR = Path(__file__).parent.parent
LOG_DIR = SKILL_DIR / "logs"
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"

class DebugHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self._json_response({"status": "ok", "timestamp": datetime.now().isoformat()})
            
        elif self.path == '/logs':
            # List all log files
            logs = []
            if LOG_DIR.exists():
                for f in sorted(LOG_DIR.glob("*.log"), reverse=True)[:10]:
                    logs.append({
                        "name": f.name,
                        "size": f.stat().st_size,
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    })
            self._json_response({"logs": logs})
            
        elif self.path.startswith('/logs/'):
            # Return specific log file
            log_name = self.path.replace('/logs/', '').replace('..', '')  # Sanitize
            log_file = LOG_DIR / log_name
            
            if log_file.exists() and log_file.suffix == '.log':
                try:
                    content = log_file.read_text()
                    # Return last 500 lines
                    lines = content.split('\n')[-500:]
                    self._text_response('\n'.join(lines))
                except Exception as e:
                    self._error_response(str(e))
            else:
                self._error_response("Log not found", 404)
                
        elif self.path == '/status':
            # Pipeline status
            status = {
                "timestamp": datetime.now().isoformat(),
                "log_dir_exists": LOG_DIR.exists(),
                "pipeline_dir_exists": PIPELINE_DIR.exists(),
            }
            
            if PIPELINE_DIR.exists():
                lead_files = list(PIPELINE_DIR.glob("leads_*.json"))
                status["lead_files"] = len(lead_files)
                if lead_files:
                    latest = max(lead_files, key=lambda x: x.stat().st_mtime)
                    status["last_run"] = datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
            
            self._json_response(status)
            
        elif self.path == '/':
            self._html_response("""
            <h1>Nexus Debug</h1>
            <ul>
                <li><a href="/logs">/logs</a> - List log files</li>
                <li><a href="/logs/startup.log">/logs/startup.log</a> - Startup log</li>
                <li><a href="/status">/status</a> - Pipeline status</li>
                <li><a href="/health">/health</a> - Health check</li>
            </ul>
            """)
        else:
            self._error_response("Not found", 404)
    
    def _json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _text_response(self, text):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode())
    
    def _html_response(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _error_response(self, msg, code=500):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode())
    
    def log_message(self, format, *args):
        pass

def run_server(port=8000):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    server = HTTPServer(('0.0.0.0', port), DebugHandler)
    print(f"Debug server on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    run_server(port)
