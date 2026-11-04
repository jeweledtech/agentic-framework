#!/usr/bin/env python3
"""
JeweledTech Agentic Framework API Server

A simple, developer-friendly API server for creating and orchestrating AI agents.
This server demonstrates the core capabilities of the framework.
"""

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Version from single source of truth
try:
    from core._version import __version__
except ImportError:
    __version__ = "0.0.0-dev"

# Import framework components
from agents.examples import ResearchAgent, WriterAgent
from agents.executive_chat import ExecutiveChatAgent
from core.audit import AuditEvent, AuditEventType, get_audit_logger
from core.auth import (
    AuthNotConfiguredError,
    Principal,
    auth_enabled,
    authenticate,
    current_principal,
    load_api_keys,
)
from core.security import Permission, role_has_permission
from core.approvals import ApprovalError, ApprovalStatus, get_approval_queue
from contextlib import asynccontextmanager

try:
    from core.crew import CrewBuilder, CREWAI_AVAILABLE
except ImportError:
    CrewBuilder = None
    CREWAI_AVAILABLE = False

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Refuse to start with auth enabled but no API keys (fail closed)."""
    if auth_enabled():
        if not load_api_keys():
            raise RuntimeError(
                "Authentication is enabled but no API key is configured. "
                "Set FRAMEWORK_API_KEYS='key:department,...' (or FRAMEWORK_API_KEY), "
                "or set ENABLE_AUTH=false for local development only."
            )
    else:
        logger.warning("ENABLE_AUTH=false: API authentication is DISABLED. "
                       "Do not run this configuration outside local development.")
    yield


# Initialize FastAPI app
app = FastAPI(
    title="JeweledTech Agentic Framework",
    description="Open-source framework for building multi-agent AI systems",
    version=__version__,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit middleware — logs every request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every API request to the audit log."""

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000

        audit = get_audit_logger()
        audit.log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            client_ip=request.client.host if request.client else "",
            details={"duration_ms": round(duration_ms, 2)},
        )
        return response


app.add_middleware(AuditMiddleware)

# API Key Security
# Every route except "/" and "/health" depends on require(<permission>).
# tests/api/test_route_protection.py enumerates all routes to enforce this.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_principal(request: Request, api_key: Optional[str] = Security(api_key_header)) -> Principal:
    """Authenticate the caller. 401 for a missing/invalid key, 503 if no keys exist."""
    try:
        principal = authenticate(api_key)
    except AuthNotConfiguredError:
        raise HTTPException(status_code=503,
                            detail="Authentication is enabled but no API keys are configured")
    if principal is None:
        get_audit_logger().log(AuditEvent(
            event_type=AuditEventType.API_AUTH_FAILURE,
            actor_id=request.client.host if request.client else "",
            action="api.auth",
            resource=request.url.path,
            details={"key_present": bool(api_key)},
            outcome="failure",
        ))
        raise HTTPException(status_code=401, detail="Invalid or missing API key",
                            headers={"WWW-Authenticate": "ApiKey"})
    current_principal.set(principal)
    return principal


# Backwards-compatible name
verify_api_key = get_principal


def require(permission: Permission, department: Optional[str] = None):
    """Dependency: caller must hold *permission* (and belong to *department*,
    unless their role has cross-department API_ALL)."""

    async def dependency(request: Request, principal: Principal = Depends(get_principal)) -> Principal:
        allowed = role_has_permission(principal.role, permission)
        if allowed and department and principal.department != department:
            allowed = role_has_permission(principal.role, Permission.API_ALL)
        if not allowed:
            get_audit_logger().log_permission_denied(
                actor_id=principal.key_id,
                department=principal.department,
                permission=permission.value,
                resource=request.url.path,
            )
            scope = f" for department '{department}'" if department else ""
            raise HTTPException(status_code=403,
                                detail=f"Permission denied: requires {permission.value}{scope}")
        return principal

    return dependency


def session_for(principal: Principal, conversation_id: Optional[str]) -> str:
    """Chat sessions are scoped to the calling key."""
    return f"{principal.key_id}:{conversation_id or 'default'}"


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

class ResetRequest(BaseModel):
    conversation_id: Optional[str] = None

class RejectRequest(BaseModel):
    reason: str = ""

class AgentResponse(BaseModel):
    agent: str
    task: str
    result: Any
    timestamp: str
    status: str

# n8n Integration Request Models
class N8NWebhookRequest(BaseModel):
    """Request model for n8n webhook calls"""
    workflow_id: str
    trigger_type: str  # "sales", "marketing", "research", "custom"
    payload: Dict[str, Any]
    callback_url: Optional[str] = None

class SalesLeadRequest(BaseModel):
    """Request model for sales lead processing"""
    lead_name: str
    lead_email: str
    lead_company: str
    lead_source: str = "n8n"
    additional_data: Optional[Dict[str, Any]] = None

class SalesQualifyRequest(BaseModel):
    """Request model for lead qualification"""
    lead_id: str
    lead_data: Dict[str, Any]
    icp_criteria: Optional[Dict[str, Any]] = None

class MarketingRequest(BaseModel):
    """Request model for marketing actions"""
    action: str  # "generate_content", "analyze", "distribute"
    campaign_name: Optional[str] = None
    parameters: Dict[str, Any]

# API Routes
@app.get("/")
def read_root():
    """Welcome endpoint with framework information"""
    return {
        "framework": "JeweledTech Agentic Framework",
        "version": __version__,
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
def list_agents(principal: Principal = Depends(require(Permission.API_READ))):
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
async def research_topic(request: ResearchRequest, principal: Principal = Depends(require(Permission.AGENT_EXECUTE))):
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
async def write_content(request: WritingRequest, principal: Principal = Depends(require(Permission.AGENT_EXECUTE))):
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
async def collaborate_agents(request: CollaborativeRequest, principal: Principal = Depends(require(Permission.AGENT_EXECUTE))):
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
async def create_crew(
    agent_ids: List[str],
    crew_name: str = "Custom Crew",
    principal: Principal = Depends(require(Permission.AGENT_CREATE)),
):
    """
    Create a crew of agents for complex tasks.
    Requires CrewAI to be installed (pip install -r requirements-crewai.txt).
    """
    if not CREWAI_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail={
                "error": "CrewAI not installed",
                "message": "Crew orchestration requires CrewAI. Install with: pip install -r requirements-crewai.txt",
                "alternatives": [
                    "Use /research, /write, /collaborate endpoints (work without CrewAI)",
                    "Use /chat for general agent interactions"
                ]
            }
        )
    try:
        # Map agent IDs to actual agents
        agent_map = {
            "research_agent": research_agent,
            "writer_agent": writer_agent
        }

        agents = [agent_map.get(aid) for aid in agent_ids if aid in agent_map]

        if not agents:
            raise ValueError("No valid agents specified")

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
async def executive_chat(request: ChatRequest, principal: Principal = Depends(require(Permission.AGENT_EXECUTE))):
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
            },
            session_id=session_for(principal, request.conversation_id),
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
async def analyze_business_request(request: Dict[str, Any], principal: Principal = Depends(require(Permission.AGENT_EXECUTE))):
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
async def reset_chat(
    request: Optional[ResetRequest] = None,
    principal: Principal = Depends(require(Permission.AGENT_EXECUTE)),
):
    """Reset the caller's own conversation history (other callers are unaffected)."""
    conversation_id = request.conversation_id if request else None
    executive_chat_agent.reset_conversation(session_for(principal, conversation_id))
    return {"status": "success", "message": "Conversation history reset"}

# ============================================================
# n8n Integration Endpoints
# ============================================================

@app.post("/n8n/webhook")
async def n8n_webhook(
    request: N8NWebhookRequest,
    principal: Principal = Depends(require(Permission.API_WRITE))
):
    """
    Generic webhook endpoint for n8n workflows.
    Routes requests to appropriate agents based on trigger_type.
    """
    try:
        logger.info(f"n8n webhook received: {request.trigger_type} from workflow {request.workflow_id}")

        if request.trigger_type == "sales":
            # Route to sales processing
            result = await process_sales_webhook(request.payload)
        elif request.trigger_type == "marketing":
            # Route to marketing processing
            result = await process_marketing_webhook(request.payload)
        elif request.trigger_type == "research":
            # Use research agent
            result = research_agent.research_topic(
                topic=request.payload.get("topic", ""),
                depth=request.payload.get("depth", "medium")
            )
        else:
            # Custom processing via executive chat
            result = executive_chat_agent.chat(
                message=str(request.payload),
                context={"workflow_id": request.workflow_id, "source": "n8n"},
                session_id=session_for(principal, f"n8n:{request.workflow_id}"),
            )

        return {
            "status": "success",
            "workflow_id": request.workflow_id,
            "trigger_type": request.trigger_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"n8n webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_sales_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process sales-related webhook payloads"""
    action = payload.get("action", "process")
    if action == "qualify":
        return {
            "qualified": True,
            "score": 85,
            "recommendation": "High-priority lead - schedule demo",
            "next_steps": ["Send personalized email", "Schedule discovery call"]
        }
    return {
        "processed": True,
        "action": action,
        "message": f"Sales action '{action}' processed successfully"
    }

async def process_marketing_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process marketing-related webhook payloads"""
    action = payload.get("action", "analyze")
    if action == "generate_content":
        topic = payload.get("topic", "")
        content = writer_agent.write_blog_post(
            topic=topic,
            tone="professional",
            word_count=500
        )
        return {"content": content, "topic": topic}
    return {
        "processed": True,
        "action": action,
        "message": f"Marketing action '{action}' processed successfully"
    }

@app.post("/sales/process-lead")
async def process_lead(
    request: SalesLeadRequest,
    principal: Principal = Depends(require(Permission.AGENT_EXECUTE, department="sales"))
):
    """
    Process a new sales lead from n8n CRM integration.
    Analyzes the lead and provides qualification recommendations.
    """
    try:
        logger.info(f"Processing lead: {request.lead_name} from {request.lead_company}")

        # Use executive chat for intelligent lead analysis
        analysis_prompt = f"""
        Analyze this sales lead and provide qualification recommendations:
        - Name: {request.lead_name}
        - Email: {request.lead_email}
        - Company: {request.lead_company}
        - Source: {request.lead_source}
        - Additional Data: {request.additional_data or 'None'}

        Provide: qualification score (1-100), priority level, recommended next steps.
        """

        response = executive_chat_agent.chat(
            message=analysis_prompt,
            context={"lead_source": request.lead_source, "type": "lead_analysis"},
            session_id=session_for(principal, "lead_analysis"),
        )

        return {
            "status": "success",
            "lead": {
                "name": request.lead_name,
                "email": request.lead_email,
                "company": request.lead_company
            },
            "analysis": response.get("message", "Analysis complete"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Lead processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sales/qualify-lead")
async def qualify_lead(
    request: SalesQualifyRequest,
    principal: Principal = Depends(require(Permission.AGENT_EXECUTE, department="sales"))
):
    """
    Qualify a lead against ICP (Ideal Customer Profile) criteria.
    """
    try:
        default_icp = {
            "company_size": "50-500 employees",
            "industry": ["technology", "finance", "healthcare"],
            "budget_range": "$10k-$100k",
            "decision_timeline": "1-3 months"
        }

        icp = request.icp_criteria or default_icp

        # Score the lead against ICP
        qualification_prompt = f"""
        Qualify this lead against our ICP criteria:

        Lead Data: {request.lead_data}

        ICP Criteria: {icp}

        Provide a qualification score (0-100), match reasons, and gaps.
        """

        response = executive_chat_agent.chat(
            message=qualification_prompt,
            context={"type": "icp_qualification"},
            session_id=session_for(principal, "icp_qualification"),
        )

        return {
            "status": "success",
            "lead_id": request.lead_id,
            "qualification": response.get("message", "Qualification complete"),
            "icp_criteria_used": icp,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Lead qualification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/marketing/generate-content")
async def generate_marketing_content(
    request: MarketingRequest,
    principal: Principal = Depends(require(Permission.AGENT_EXECUTE, department="marketing"))
):
    """
    Generate marketing content using AI agents.
    Supports: blog posts, social media, email campaigns.
    """
    try:
        if request.action != "generate_content":
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {request.action}. Use 'generate_content' for this endpoint."
            )

        content_type = request.parameters.get("content_type", "blog_post")
        topic = request.parameters.get("topic", "")
        tone = request.parameters.get("tone", "professional")
        word_count = request.parameters.get("word_count", 800)

        if content_type == "blog_post":
            result = writer_agent.write_blog_post(
                topic=topic,
                tone=tone,
                word_count=word_count
            )
        elif content_type == "social_media":
            result = writer_agent.write_email(  # Repurpose for short content
                subject=topic,
                tone="engaging",
                key_points=request.parameters.get("key_points", [topic])
            )
        else:
            result = writer_agent.summarize_content(
                content=topic,
                max_words=word_count
            )

        return {
            "status": "success",
            "campaign_name": request.campaign_name,
            "content_type": content_type,
            "content": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/marketing/analyze-campaign")
async def analyze_campaign(
    request: MarketingRequest,
    principal: Principal = Depends(require(Permission.AGENT_EXECUTE, department="marketing"))
):
    """
    Analyze marketing campaign performance.
    """
    try:
        if request.action != "analyze":
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {request.action}. Use 'analyze' for this endpoint."
            )

        campaign_data = request.parameters.get("campaign_data", {})

        analysis_prompt = f"""
        Analyze this marketing campaign and provide insights:

        Campaign: {request.campaign_name or 'Unnamed Campaign'}
        Data: {campaign_data}

        Provide: performance summary, key insights, recommendations for improvement.
        """

        response = executive_chat_agent.chat(
            message=analysis_prompt,
            context={"type": "campaign_analysis"},
            session_id=session_for(principal, "campaign_analysis"),
        )

        return {
            "status": "success",
            "campaign_name": request.campaign_name,
            "analysis": response.get("message", "Analysis complete"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Campaign analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Human approval of agent actions
# ============================================================

@app.get("/approvals")
async def list_approvals(
    status: Optional[ApprovalStatus] = None,
    principal: Principal = Depends(require(Permission.API_ADMIN)),
):
    """List agent actions waiting for (or decided by) a human approver."""
    return {"approvals": [a.to_dict() for a in get_approval_queue().list(status=status)]}


@app.post("/approvals/{action_id}/approve")
async def approve_action(
    action_id: str,
    principal: Principal = Depends(require(Permission.API_ADMIN)),
):
    """Approve a pending action. It executes once, immediately."""
    try:
        return get_approval_queue().approve(action_id, approver=principal.key_id).to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown approval id")
    except ApprovalError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/approvals/{action_id}/reject")
async def reject_action(
    action_id: str,
    request: Optional[RejectRequest] = None,
    principal: Principal = Depends(require(Permission.API_ADMIN)),
):
    """Reject a pending action. It will never execute."""
    try:
        return get_approval_queue().reject(
            action_id, approver=principal.key_id,
            reason=request.reason if request else "",
        ).to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown approval id")
    except ApprovalError as e:
        raise HTTPException(status_code=409, detail=str(e))


def main():
    """Entry point for the agentic-server CLI command."""
    import uvicorn

    print("\n" + "="*60)
    print(f"[*] JeweledTech Agentic Framework v{__version__}")
    print("="*60)
    print("\nStarting API server...")
    print("Documentation available at: http://localhost:8000/docs")
    print("\nExample agents loaded:")
    print("  [+] Research Agent - For researching topics")
    print("  [+] Writer Agent - For content creation")
    print("  [+] Executive Chat - AI-powered conversational interface")
    print("\n[TIP] Try the /collaborate endpoint to see agents working together!")
    print("\n[INFO] Need production-ready agents? Visit https://jeweledtech.com/enterprise")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


# Run the server
if __name__ == "__main__":
    main()