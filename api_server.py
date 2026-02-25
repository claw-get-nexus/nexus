#!/usr/bin/env python3
"""
Nexus API Server — Render Deployment Ready
FastAPI app serving the AI agent and demo.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
import sys

sys.path.insert(0, '/root/.openclaw/skills/nexus-core')
from core_agent import NexusCoreAgent

app = FastAPI(title="Nexus Automation API")

# Initialize agent
agent = NexusCoreAgent(config={
    "confidence_threshold": 0.7,
    "escalation_threshold": 0.5
})

# Request/Response models
class TicketRequest(BaseModel):
    id: str
    text: str
    customer_name: Optional[str] = "Customer"

class TicketResponse(BaseModel):
    ticket_id: str
    action_taken: str
    confidence: float
    response: Optional[str] = None
    requires_human: bool

# API Routes
@app.post("/api/v1/ticket", response_model=TicketResponse)
async def process_ticket(ticket: TicketRequest):
    """Process a support ticket through the AI agent"""
    try:
        result = agent.process_ticket(ticket.dict())
        return TicketResponse(
            ticket_id=result["ticket_id"],
            action_taken=result["action_taken"],
            confidence=result["confidence"],
            response=result.get("response"),
            requires_human=result["requires_human"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "ready"}

# Demo page
@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Serve the interactive demo"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus AI Agent Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .logo {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 10px;
        }
        .tagline { text-align: center; color: #64748b; margin-bottom: 40px; }
        .demo-box {
            background: #1e293b;
            border-radius: 16px;
            padding: 30px;
            border: 1px solid #334155;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            color: #94a3b8;
            font-size: 14px;
        }
        .input-group input,
        .input-group textarea {
            width: 100%;
            padding: 12px;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #e2e8f0;
            font-size: 14px;
        }
        .input-group textarea {
            min-height: 100px;
            resize: vertical;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn:hover { opacity: 0.9; }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #0f172a;
            border-radius: 12px;
            border: 1px solid #334155;
            display: none;
        }
        .result.show { display: block; }
        .result-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #334155;
        }
        .intent-badge {
            background: #3b82f6;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
        .confidence {
            color: #64748b;
            font-size: 14px;
        }
        .response-box {
            background: #1e293b;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #22c55e;
        }
        .response-label {
            font-size: 12px;
            color: #22c55e;
            margin-bottom: 8px;
        }
        .loading {
            text-align: center;
            color: #64748b;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚡ Nexus AI Agent</div>
        <div class="tagline">Try our AI support agent with a test ticket</div>
        
        <div class="demo-box">
            <div class="input-group">
                <label>Your Name</label>
                <input type="text" id="name" placeholder="John Doe" value="Test Customer">
            </div>
            
            <div class="input-group">
                <label>Support Ticket</label>
                <textarea id="ticket" placeholder="I forgot my password and can't login...">I forgot my password and can't access my account. I have an important meeting in 30 minutes.</textarea>
            </div>
            
            <button class="btn" onclick="submitTicket()">Process with AI Agent →</button>
            
            <div class="loading" id="loading">Processing...</div>
            
            <div class="result" id="result">
                <div class="result-header">
                    <span class="intent-badge" id="intent">password_reset</span>
                    <span class="confidence" id="confidence">Confidence: 85%</span>
                </div>
                <div>
                    <strong>Action:</strong> <span id="action">Automated Response</span>
                </div>
                <div class="response-box">
                    <div class="response-label">🤖 AI Agent Response</div>
                    <div id="response"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        async function submitTicket() {
            const name = document.getElementById('name').value;
            const text = document.getElementById('ticket').value;
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            loading.style.display = 'block';
            result.classList.remove('show');
            
            try {
                const response = await fetch('/api/v1/ticket', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: 'DEMO_' + Date.now(),
                        text: text,
                        customer_name: name
                    })
                });
                
                const data = await response.json();
                
                document.getElementById('intent').textContent = data.intent || 'unknown';
                document.getElementById('confidence').textContent = 'Confidence: ' + Math.round(data.confidence * 100) + '%';
                document.getElementById('action').textContent = data.action_taken;
                document.getElementById('response').textContent = data.response || 'Escalated to human agent';
                
                result.classList.add('show');
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                loading.style.display = 'none';
            }
        }
    </script>
</body>
</html>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to main website"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=https://get-nexus.app">
    </head>
    <body>Redirecting...</body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
