#!/usr/bin/env python3
"""
Nexus Automation — Dynamic Execution Endpoint
Downloads and executes code from URL (bypasses deploy cache).
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

SKILL_DIR = Path(__file__).parent.parent

def download_and_run(url: str) -> dict:
    """Download Python code from URL and execute it."""
    try:
        # Download code
        with urllib.request.urlopen(url, timeout=30) as response:
            code = response.read().decode('utf-8')
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        # Execute in subprocess with fresh environment
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(SKILL_DIR),
            env=env
        )
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",  # Last 2000 chars
            "stderr": result.stderr[-1000:] if result.stderr else "",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"status": "exception", "error": str(e), "timestamp": datetime.now().isoformat()}

class DynamicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "timestamp": datetime.now().isoformat()}).encode())
            
        elif self.path.startswith('/exec?url='):
            # Extract URL from query string
            import urllib.parse
            query = self.path.split('?')[1] if '?' in self.path else ''
            params = urllib.parse.parse_qs(query)
            url = params.get('url', [''])[0]
            
            if not url:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing url parameter")
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            result = download_and_run(url)
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def run_server(port=8000):
    server = HTTPServer(('0.0.0.0', port), DynamicHandler)
    print(f"Dynamic execution server on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    run_server(port)
