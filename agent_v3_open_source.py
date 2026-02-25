#!/usr/bin/env python3
"""
Nexus AI Agent v3 — Fully Open Source
Ollama + BGE + Chroma + LlamaIndex
No API keys. No cloud dependencies.
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

# LlamaIndex for RAG orchestration
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever

# Chroma for vector storage
import chromadb
from chromadb.config import Settings as ChromaSettings

class NexusOpenSourceAgent:
    """
    Fully open source AI agent.
    Runs entirely locally. No API calls.
    """
    
    def __init__(self, knowledge_dir: str = "./knowledge"):
        self.knowledge_dir = knowledge_dir
        
        # Initialize local LLM via Ollama
        print("🦙 Loading Llama 3.1...")
        self.llm = Ollama(
            model="llama3.1:8b",
            temperature=0.3,
            request_timeout=60.0
        )
        
        # Initialize local embeddings (BGE)
        print("🔢 Loading BGE embeddings...")
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        # Configure LlamaIndex
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        
        # Initialize Chroma
        print("💾 Initializing Chroma...")
        self.chroma_client = chromadb.Client(
            ChromaSettings(
                persist_directory="./chroma_db",
                anonymized_telemetry=False
            )
        )
        
        # Load or create index
        self.index = self._load_or_create_index()
        print("✅ Agent ready (fully local)")
    
    def _load_or_create_index(self) -> VectorStoreIndex:
        """Load existing index or create from knowledge base"""
        
        # Check if we have a persisted index
        if os.path.exists("./storage"):
            from llama_index.core import StorageContext, load_index_from_storage
            storage_context = StorageContext.from_defaults(persist_dir="./storage")
            return load_index_from_storage(storage_context)
        
        # Create new index from knowledge directory
        if os.path.exists(self.knowledge_dir):
            documents = SimpleDirectoryReader(self.knowledge_dir).load_data()
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist()
            return index
        
        # Empty index if no knowledge yet
        return VectorStoreIndex([])
    
    def add_knowledge(self, text: str, metadata: Dict = None):
        """Add new knowledge to the agent"""
        from llama_index.core import Document
        
        doc = Document(text=text, metadata=metadata or {})
        self.index.insert(doc)
        self.index.storage_context.persist()
    
    def classify_intent(self, ticket_text: str) -> Dict:
        """Use local LLM to classify intent"""
        
        prompt = f"""Analyze this support ticket and classify it.

Ticket: {ticket_text}

Classify into ONE of these categories:
- password_reset
- billing_issue  
- technical_support
- account_access
- feature_request
- general_inquiry

Also rate confidence (0.0-1.0) and urgency (low/medium/high).

Respond in JSON format:
{{"intent": "category", "confidence": 0.85, "urgency": "medium"}}"""

        response = self.llm.complete(prompt)
        
        try:
            # Parse JSON from response
            result = json.loads(response.text)
            return result
        except:
            # Fallback
            return {
                "intent": "general_inquiry",
                "confidence": 0.5,
                "urgency": "low"
            }
    
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant context from knowledge base"""
        
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k
        )
        
        nodes = retriever.retrieve(query)
        
        if not nodes:
            return "No relevant knowledge found."
        
        context = "\n\n".join([n.node.text for n in nodes])
        return context
    
    def generate_response(self, ticket: Dict, intent: Dict, context: str) -> Dict:
        """Generate AI response using RAG"""
        
        prompt = f"""You are Nexus AI, a helpful customer support agent.

TICKET FROM {ticket.get('customer_name', 'Customer')}:
{ticket['text']}

CLASSIFIED INTENT: {intent['intent']} (confidence: {intent['confidence']})
URGENCY: {intent['urgency']}

RELEVANT KNOWLEDGE:
{context}

INSTRUCTIONS:
- Use the knowledge to provide an accurate answer
- Be concise, friendly, and professional
- If you can't answer confidently, say you'll escalate to a human
- Include specific steps when applicable

DRAFT YOUR RESPONSE:"""

        response = self.llm.complete(prompt)
        
        # Determine action based on confidence
        confidence = intent['confidence']
        if confidence > 0.8:
            action = "automate"
        elif confidence > 0.5:
            action = "draft_for_review"
        else:
            action = "escalate"
        
        return {
            "response": response.text,
            "action": action,
            "confidence": confidence
        }
    
    def process_ticket(self, ticket: Dict) -> Dict:
        """Full pipeline: classify → retrieve → generate"""
        
        print(f"🎫 Processing ticket: {ticket.get('id', 'unknown')}")
        
        # Step 1: Classify intent
        print("  → Classifying intent...")
        intent = self.classify_intent(ticket['text'])
        print(f"    Intent: {intent['intent']} ({intent['confidence']:.2f})")
        
        # Step 2: Retrieve context
        print("  → Retrieving knowledge...")
        context = self.retrieve_context(ticket['text'])
        print(f"    Found {len(context)} chars of context")
        
        # Step 3: Generate response
        print("  → Generating response...")
        result = self.generate_response(ticket, intent, context)
        print(f"    Action: {result['action']}")
        
        return {
            "ticket_id": ticket.get('id'),
            "intent": intent['intent'],
            "confidence": intent['confidence'],
            "urgency": intent['urgency'],
            "action": result['action'],
            "response": result['response'],
            "context_snippet": context[:200] + "..." if len(context) > 200 else context,
            "timestamp": datetime.now().isoformat(),
            "model": "llama3.1:8b",
            "stack": "fully_open_source"
        }

# FastAPI app
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Nexus AI Agent — Open Source")

# Initialize agent (this will download models on first run)
print("🚀 Starting Nexus Open Source Agent...")
agent = NexusOpenSourceAgent()

class TicketRequest(BaseModel):
    id: str
    text: str
    customer_name: Optional[str] = "Customer"

@app.post("/api/v3/ticket")
async def process_ticket(ticket: TicketRequest):
    """Process ticket with fully open source AI agent"""
    result = agent.process_ticket(ticket.dict())
    return result

@app.get("/api/v3/health")
async def health():
    return {
        "status": "healthy",
        "agent": "Nexus Open Source v3",
        "llm": "llama3.1:8b",
        "embeddings": "BGE-small-en-v1.5",
        "vector_db": "Chroma",
        "stack": "fully_local"
    }

@app.get("/")
async def root():
    return {
        "name": "Nexus AI Agent",
        "version": "3.0.0",
        "stack": "fully_open_source",
        "endpoints": {
            "process_ticket": "/api/v3/ticket",
            "health": "/api/v3/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
