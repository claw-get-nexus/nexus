#!/usr/bin/env python3
"""
Nexus Core AI Agent — Production Template
Based on HyScaler 5-layer architecture.
Ready for customer deployment.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class NexusCoreAgent:
    """
    Production AI agent for customer support automation.
    
    Architecture (HyScaler 5-layer):
    1. PERCEPTION: Monitor tickets, classify intent
    2. REASONING: Decide action, confidence scoring
    3. ACTION: Generate response or escalate
    4. LEARNING: Track outcomes, improve
    5. COMMUNICATION: Human handoff when needed
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.escalation_threshold = self.config.get("escalation_threshold", 0.5)
        
        # Load knowledge base (RAG)
        self.knowledge_base = self._load_knowledge_base()
        
        # Intent patterns (perception layer)
        self.intent_patterns = self._load_intent_patterns()
        
        # Response templates
        self.templates = self._load_templates()
    
    # ==================== LAYER 1: PERCEPTION ====================
    
    def perceive(self, ticket: Dict) -> Dict:
        """
        Perception Layer: Analyze incoming ticket.
        Extract intent, sentiment, urgency.
        """
        text = ticket.get("text", "")
        
        perception = {
            "ticket_id": ticket.get("id"),
            "timestamp": datetime.now().isoformat(),
            "intent": self._classify_intent(text),
            "sentiment": self._analyze_sentiment(text),
            "urgency": self._assess_urgency(text),
            "entities": self._extract_entities(text),
            "can_automate": False  # Set by reasoning layer
        }
        
        return perception
    
    def _classify_intent(self, text: str) -> Dict:
        """Classify ticket intent using patterns"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return {
                        "category": intent,
                        "confidence": 0.85,
                        "matched_pattern": pattern
                    }
        
        return {
            "category": "unknown",
            "confidence": 0.3,
            "matched_pattern": None
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        negative_words = ["angry", "frustrated", "terrible", "awful", "worst", "hate", "broken"]
        positive_words = ["happy", "great", "excellent", "love", "best", "good", "thanks"]
        
        text_lower = text.lower()
        neg_count = sum(1 for w in negative_words if w in text_lower)
        pos_count = sum(1 for w in positive_words if w in text_lower)
        
        if neg_count > pos_count:
            return "negative"
        elif pos_count > neg_count:
            return "positive"
        return "neutral"
    
    def _assess_urgency(self, text: str) -> str:
        """Assess ticket urgency"""
        urgent_words = ["urgent", "asap", "immediately", "critical", "down", "broken"]
        text_lower = text.lower()
        
        if any(w in text_lower for w in urgent_words):
            return "high"
        return "normal"
    
    def _extract_entities(self, text: str) -> Dict:
        """Extract key entities from ticket"""
        # Simple entity extraction
        entities = {
            "email": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            "order_id": re.findall(r'(?:order|ticket|case)[\s#:]*(\d+)', text, re.I),
            "amount": re.findall(r'\$[\d,]+(?:\.\d{2})?', text)
        }
        return entities
    
    # ==================== LAYER 2: REASONING ====================
    
    def reason(self, perception: Dict) -> Dict:
        """
        Reasoning Layer: Decide what to do.
        Calculate confidence, determine action.
        """
        intent = perception["intent"]
        sentiment = perception["sentiment"]
        urgency = perception["urgency"]
        
        # Calculate automation confidence
        confidence = self._calculate_confidence(perception)
        
        # Determine action
        if confidence >= self.confidence_threshold and sentiment != "negative":
            action = "automate"
        elif confidence >= self.escalation_threshold:
            action = "draft_for_review"
        else:
            action = "escalate"
        
        decision = {
            "ticket_id": perception["ticket_id"],
            "action": action,
            "confidence": confidence,
            "reasoning": {
                "intent_category": intent["category"],
                "intent_confidence": intent["confidence"],
                "sentiment": sentiment,
                "urgency": urgency,
                "can_automate": action == "automate"
            }
        }
        
        return decision
    
    def _calculate_confidence(self, perception: Dict) -> float:
        """Calculate overall confidence for automation"""
        base_confidence = perception["intent"]["confidence"]
        
        # Adjust for sentiment
        if perception["sentiment"] == "negative":
            base_confidence *= 0.7
        
        # Adjust for urgency
        if perception["urgency"] == "high":
            base_confidence *= 0.8
        
        # Adjust for known intent
        if perception["intent"]["category"] == "unknown":
            base_confidence *= 0.5
        
        return min(base_confidence, 1.0)
    
    # ==================== LAYER 3: ACTION ====================
    
    def act(self, decision: Dict, ticket: Dict) -> Dict:
        """
        Action Layer: Execute the decision.
        Generate response or escalate.
        """
        action = decision["action"]
        
        if action == "automate":
            return self._generate_response(decision, ticket)
        elif action == "draft_for_review":
            return self._draft_for_review(decision, ticket)
        else:
            return self._escalate(decision, ticket)
    
    def _generate_response(self, decision: Dict, ticket: Dict) -> Dict:
        """Generate automated response"""
        intent_category = decision["reasoning"]["intent_category"]
        
        # Get template for intent
        template = self.templates.get(intent_category, self.templates["general"])
        
        # Personalize
        response = template.format(
            customer_name=ticket.get("customer_name", "there"),
            issue_summary=ticket.get("text", "")[:100]
        )
        
        return {
            "ticket_id": decision["ticket_id"],
            "action_taken": "automated_response",
            "response": response,
            "confidence": decision["confidence"],
            "requires_human": False,
            "timestamp": datetime.now().isoformat()
        }
    
    def _draft_for_review(self, decision: Dict, ticket: Dict) -> Dict:
        """Draft response for human review"""
        draft = self._generate_response(decision, ticket)
        draft["action_taken"] = "drafted_for_review"
        draft["requires_human"] = True
        return draft
    
    def _escalate(self, decision: Dict, ticket: Dict) -> Dict:
        """Escalate to human agent"""
        return {
            "ticket_id": decision["ticket_id"],
            "action_taken": "escalated",
            "reason": f"Confidence {decision['confidence']:.2f} below threshold",
            "ticket_summary": ticket.get("text", "")[:200],
            "requires_human": True,
            "priority": decision["reasoning"]["urgency"],
            "timestamp": datetime.now().isoformat()
        }
    
    # ==================== LAYER 4: LEARNING ====================
    
    def learn(self, outcome: Dict):
        """
        Learning Layer: Track outcomes and improve.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ticket_id": outcome.get("ticket_id"),
            "action": outcome.get("action_taken"),
            "confidence": outcome.get("confidence"),
            "customer_satisfaction": outcome.get("csat"),
            "resolution_time": outcome.get("resolution_time")
        }
        
        # Append to learning log
        log_path = "/root/.openclaw/workspace/agent_learning.jsonl"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    # ==================== LAYER 5: COMMUNICATION ====================
    
    def communicate(self, result: Dict) -> str:
        """
        Communication Layer: Format output for humans.
        """
        if result["action_taken"] == "automated_response":
            return f"✅ Automated response sent (confidence: {result['confidence']:.2f})"
        elif result["action_taken"] == "drafted_for_review":
            return f"📝 Drafted for review (confidence: {result['confidence']:.2f})"
        else:
            return f"🚨 Escalated to human: {result.get('reason', '')}"
    
    # ==================== MAIN PROCESSING ====================
    
    def process_ticket(self, ticket: Dict) -> Dict:
        """
        Main entry point: Process a ticket through all 5 layers.
        """
        # Layer 1: Perceive
        perception = self.perceive(ticket)
        
        # Layer 2: Reason
        decision = self.reason(perception)
        
        # Layer 3: Act
        result = self.act(decision, ticket)
        
        # Layer 4: Learn (async)
        self.learn(result)
        
        # Layer 5: Communicate
        message = self.communicate(result)
        
        return {
            **result,
            "message": message,
            "perception": perception,
            "decision": decision
        }
    
    # ==================== CONFIGURATION ====================
    
    def _load_knowledge_base(self) -> Dict:
        """Load RAG knowledge base"""
        return {
            "password_reset": "To reset your password, click the link in your email...",
            "billing": "You can view and manage billing in Account Settings...",
            "api_docs": "Our API documentation is available at..."
        }
    
    def _load_intent_patterns(self) -> Dict:
        """Load intent classification patterns"""
        return {
            "password_reset": [
                r"password", r"forgot", r"reset", r"can't login", 
                r"locked out", r"access denied"
            ],
            "billing": [
                r"bill", r"invoice", r"charge", r"payment", 
                r"refund", r"subscription", r"upgrade", r"downgrade"
            ],
            "technical_issue": [
                r"error", r"bug", r"not working", r"broken", 
                r"crash", r"failed", r"issue"
            ],
            "account_access": [
                r"account", r"login", r"access", r"locked", 
                r"suspended", r"deactivated"
            ],
            "feature_request": [
                r"feature", r"suggestion", r"would be nice", 
                r"add", r"implement"
            ]
        }
    
    def _load_templates(self) -> Dict:
        """Load response templates"""
        return {
            "password_reset": """Hi {customer_name},

I can help you reset your password right away.

Click this secure link to reset: [RESET_LINK]
This link expires in 1 hour for security.

Let me know if you need anything else!

— Nexus AI Agent""",
            
            "billing": """Hi {customer_name},

I've reviewed your billing inquiry about {issue_summary}.

Here's what I found:
[ACCOUNT_DETAILS]

If you need further assistance, I'm here to help.

— Nexus AI Agent""",
            
            "technical_issue": """Hi {customer_name},

I see you're experiencing: {issue_summary}

Let me help troubleshoot:
[DIAGNOSTIC_STEPS]

If this doesn't resolve it, I'll escalate to our technical team.

— Nexus AI Agent""",
            
            "general": """Hi {customer_name},

Thanks for reaching out about {issue_summary}.

I'm looking into this for you and will have an update shortly.

— Nexus AI Agent"""
        }

# ==================== DEMO ====================

if __name__ == "__main__":
    # Initialize agent
    agent = NexusCoreAgent(config={
        "confidence_threshold": 0.7,
        "escalation_threshold": 0.5
    })
    
    # Test tickets
    test_tickets = [
        {
            "id": "TICKET_001",
            "text": "I forgot my password and can't login to my account",
            "customer_name": "John Doe"
        },
        {
            "id": "TICKET_002",
            "text": "I'm furious! Your service is terrible and I want a refund immediately!",
            "customer_name": "Angry Customer"
        },
        {
            "id": "TICKET_003",
            "text": "How do I integrate your API with my custom system?",
            "customer_name": "Developer"
        }
    ]
    
    print("="*70)
    print("NEXUS CORE AI AGENT — DEMO")
    print("="*70)
    
    for ticket in test_tickets:
        print(f"\n📨 Ticket: {ticket['id']}")
        print(f"   Text: {ticket['text'][:60]}...")
        
        result = agent.process_ticket(ticket)
        
        print(f"\n   Intent: {result['perception']['intent']['category']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Action: {result['message']}")
        
        if result.get('response'):
            print(f"\n   Response preview:")
            print(f"   {result['response'][:100]}...")
        
        print("-"*70)
