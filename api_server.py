#!/usr/bin/env python3
"""
JeweledTech Agentic Framework API Server

A simple, developer-friendly API server for creating and orchestrating AI agents.
This server demonstrates the core capabilities of the framework.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import framework components
from agents.examples import ResearchAgent, WriterAgent
from agents.executive_chat import ExecutiveChatAgent
from core.crew import CrewBuilder

# Initialize FastAPI app
app = FastAPI(
    title="JeweledTech Agentic Framework",
    description="Open-source framework for building multi-agent AI systems",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize example agents
research_agent = ResearchAgent()
writer_agent = WriterAgent()
executive_chat_agent = ExecutiveChatAgent()

# Request/Response models
class ResearchRequest(BaseModel):
    topic: str
    depth: str = "medium"

class WritingRequest(BaseModel):
    topic: str
    research_data: Optional[str] = None
    tone: str = "professional"
    word_count: int = 800

class CollaborativeRequest(BaseModel):
    topic: str
    output_type: str = "blog_post"  # blog_post, documentation, report

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent: str
    task: str
    result: Any
    timestamp: str
    status: str

# API Routes
@app.get("/")
def read_root():
    """Welcome endpoint with framework information"""
    return {
        "framework": "JeweledTech Agentic Framework",
        "version": "1.0.0",
        "description": "Open-source framework for building multi-agent AI systems",
        "endpoints": {
            "/": "This welcome page",
            "/health": "Health check endpoint",
            "/agents": "List available agents",
            "/research": "Research a topic",
            "/write": "Generate written content",
            "/collaborate": "Multi-agent collaboration example",
            "/docs": "Interactive API documentation"
        },
        "enterprise": {
            "message": "Need production-ready agents and enterprise support?",
            "url": "https://jeweledtech.com/enterprise"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "framework": "JeweledTech Agentic Framework",
        "agents_loaded": 3,
        "features": ["research", "writing", "executive_chat"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents")
def list_agents():
    """List available agents and their capabilities"""
    return {
        "agents": [
            {
                "id": "research_agent",
                "name": "Research Specialist",
                "description": "Researches topics and compiles comprehensive reports",
                "capabilities": [
                    "research_topic",
                    "compare_topics", 
                    "fact_check"
                ]
            },
            {
                "id": "writer_agent",
                "name": "Content Writer",
                "description": "Creates various types of written content",
                "capabilities": [
                    "write_blog_post",
                    "create_technical_documentation",
                    "write_email",
                    "summarize_content"
                ]
            }
        ],
        "note": "These are example agents. The framework supports creating custom agents for any purpose."
    }

@app.post("/research", response_model=AgentResponse)
async def research_topic(request: ResearchRequest):
    """Research a topic using the Research Agent"""
    try:
        result = research_agent.research_topic(
            topic=request.topic,
            depth=request.depth
        )
        
        return AgentResponse(
            agent="research_agent",
            task=f"Research '{request.topic}'",
            result=result,
            timestamp=datetime.now().isoformat(),
            status="completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/write", response_model=AgentResponse)
async def write_content(request: WritingRequest):
    """Generate written content using the Writer Agent"""
    try:
        result = writer_agent.write_blog_post(
            topic=request.topic,
            research_data=request.research_data,
            tone=request.tone,
            word_count=request.word_count
        )
        
        return AgentResponse(
            agent="writer_agent",
            task=f"Write about '{request.topic}'",
            result=result,
            timestamp=datetime.now().isoformat(),
            status="completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collaborate")
async def collaborate_agents(request: CollaborativeRequest):
    """
    Demonstrate multi-agent collaboration.
    The research agent gathers information, then the writer agent creates content.
    """
    try:
        # Step 1: Research the topic
        research_result = research_agent.research_topic(
            topic=request.topic,
            depth="comprehensive"
        )
        
        # Step 2: Create content based on research
        if request.output_type == "blog_post":
            writing_result = writer_agent.write_blog_post(
                topic=request.topic,
                research_data=research_result["findings"],
                tone="professional",
                word_count=1000
            )
        elif request.output_type == "documentation":
            writing_result = writer_agent.create_technical_documentation(
                subject=request.topic,
                specifications={"based_on": "research_findings"}
            )
        else:
            writing_result = writer_agent.summarize_content(
                content=research_result["findings"],
                max_words=200
            )
        
        return {
            "collaboration": "research_and_write",
            "topic": request.topic,
            "output_type": request.output_type,
            "agents_involved": ["research_agent", "writer_agent"],
            "research_phase": research_result,
            "writing_phase": writing_result,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "enterprise_note": "This is a simple example. Enterprise version includes 20+ specialized agents working together."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crew/create")
async def create_crew(agent_ids: List[str], crew_name: str = "Custom Crew"):
    """
    Create a crew of agents for complex tasks.
    This demonstrates the crew orchestration capabilities.
    """
    try:
        # Map agent IDs to actual agents
        agent_map = {
            "research_agent": research_agent,
            "writer_agent": writer_agent
        }
        
        agents = [agent_map.get(aid) for aid in agent_ids if aid in agent_map]
        
        if not agents:
            raise ValueError("No valid agents specified")
        
        # This is a simplified example - in production, crews can execute complex workflows
        return {
            "crew_name": crew_name,
            "agents": agent_ids,
            "status": "created",
            "capabilities": "Ready to execute multi-step tasks",
            "note": "Full crew execution available in enterprise version"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat")
async def executive_chat(request: ChatRequest):
    """
    Executive Chat endpoint - AI-powered conversational interface.
    
    This provides intelligent responses for executive-level interactions,
    business strategy discussions, and decision support.
    """
    try:
        # Process the chat message
        response = executive_chat_agent.chat(
            message=request.message,
            context={
                "conversation_id": request.conversation_id,
                **(request.context or {})
            }
        )
        
        return {
            "status": "success",
            "response": response["message"],
            "metadata": response.get("metadata", {}),
            "timestamp": response["timestamp"],
            "conversation_id": request.conversation_id
        }
    except Exception as e:
        logger.error(f"Executive chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/analyze")
async def analyze_business_request(request: Dict[str, Any]):
    """
    Analyze a business request and provide structured insights.
    """
    try:
        analysis = executive_chat_agent.analyze_business_request(
            request.get("request", "")
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/reset")
async def reset_chat():
    """Reset the conversation history."""
    executive_chat_agent.reset_conversation()
    return {"status": "success", "message": "Conversation history reset"}

# Run the server
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 JeweledTech Agentic Framework")
    print("="*60)
    print("\nStarting API server...")
    print("Documentation available at: http://localhost:8000/docs")
    print("\nExample agents loaded:")
    print("  ✓ Research Agent - For researching topics")
    print("  ✓ Writer Agent - For content creation")
    print("  ✓ Executive Chat - AI-powered conversational interface")
    print("\n💡 Tip: Try the /collaborate endpoint to see agents working together!")
    print("\n🏢 Need production-ready agents? Visit https://jeweledtech.com/enterprise")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)