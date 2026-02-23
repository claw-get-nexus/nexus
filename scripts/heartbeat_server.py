#!/usr/bin/env python3
"""
Nexus Automation — Heartbeat Server
Keeps Render free instance warm + provides health endpoint.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class HeartbeatHandler(BaseHTTPRequestHandler):
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
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <h1>Nexus Automation</h1>
            <p>Autonomous business automation agency.</p>
            <p>Status: <strong>Running</strong></p>
            <p>Endpoints:
            <ul>
                <li><a href="/health">/health</a> — Health check</li>
            </ul>
            </p>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server(port=8000):
    server = HTTPServer(('0.0.0.0', port), HeartbeatHandler)
    print(f"Heartbeat server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    run_server(port)
