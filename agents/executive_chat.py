"""
Executive Chat Agent

Provides an AI-powered conversational interface for executive-level interactions,
business strategy discussions, and decision support.
"""

from collections import OrderedDict
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import threading

# Bounds on in-memory conversation state
MAX_HISTORY_PER_SESSION = 50   # messages kept per session (user + assistant)
MAX_SESSIONS = 1000            # least-recently-used sessions are evicted
DEFAULT_SESSION = "default"

# Check if we're in mock mode
USE_MOCK = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'

# Try to import base agent, fall back to standalone if not available
try:
    from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools
    BASE_AGENT_AVAILABLE = True
except ImportError:
    BASE_AGENT_AVAILABLE = False


class ExecutiveChatAgent:
    """
    Executive Chat Agent - AI-powered conversational interface.

    Provides intelligent responses for:
    - Business strategy discussions
    - Decision support
    - Executive-level queries
    - Company operations overview
    """

    def __init__(self):
        """Initialize the Executive Chat Agent"""
        # session_id -> {"history": [...], "context": {...}}; LRU-ordered
        self._sessions: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
        self._lock = threading.Lock()

        # In full mode, initialize with BaseAgent
        if BASE_AGENT_AVAILABLE and not USE_MOCK:
            try:
                config = AgentConfig(
                    id="executive_chat",
                    role=AgentRole(
                        name="Executive Assistant",
                        description="AI-powered executive assistant for business discussions",
                        goal="Provide intelligent, strategic responses to executive queries",
                        backstory="You are a seasoned executive assistant with deep business acumen."
                    ),
                    tools=AgentTools(tool_names=["knowledge_base_query"]),
                    department="admin",
                    temperature=0.7
                )
                self._base_agent = BaseAgent(config)
            except Exception:
                self._base_agent = None
        else:
            self._base_agent = None

    def _session(self, session_id: str) -> Dict[str, Any]:
        """Return (creating if needed) a session and mark it most recently used."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = {"history": [], "context": {}}
                self._sessions[session_id] = session
                while len(self._sessions) > MAX_SESSIONS:
                    self._sessions.popitem(last=False)
            else:
                self._sessions.move_to_end(session_id)
            return session

    def session_count(self) -> int:
        return len(self._sessions)

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None,
             session_id: str = DEFAULT_SESSION) -> Dict[str, Any]:
        """
        Process a chat message and return a response.

        Args:
            message: The user's message
            context: Optional context for the conversation

        Returns:
            Response dictionary with message and metadata
        """
        session = self._session(session_id)
        history = session["history"]

        # Update context
        if context:
            session["context"].update(context)

        # Add to conversation history
        history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Generate response
        if self._base_agent and not USE_MOCK:
            # Use the full agent capabilities
            response_text = self._generate_agent_response(message)
        else:
            # Use mock response for testing/demo
            response_text = self._generate_mock_response(message)

        # Add response to history
        history.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        if len(history) > MAX_HISTORY_PER_SESSION:
            del history[:-MAX_HISTORY_PER_SESSION]

        return {
            "message": response_text,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "conversation_length": len(history),
                "mode": "mock" if USE_MOCK or not self._base_agent else "full"
            }
        }

    def _generate_agent_response(self, message: str) -> str:
        """Generate response using the full agent capabilities"""
        try:
            self._base_agent.add_task(
                description=f"Respond to this executive query: {message}",
                expected_output="A helpful, professional response"
            )
            results = self._base_agent.execute_tasks()
            return results[0] if results else self._generate_mock_response(message)
        except Exception:
            return self._generate_mock_response(message)

    def _generate_mock_response(self, message: str) -> str:
        """Generate a mock response for testing/demo purposes"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your Executive AI Assistant. How can I help you today with business strategy or operations?"

        if any(word in message_lower for word in ["sales", "revenue"]):
            return "I can help you analyze sales performance and revenue trends. Our Sales department agents can provide detailed pipeline analysis and forecasting. What specific metrics would you like to explore?"

        if any(word in message_lower for word in ["marketing", "campaign"]):
            return "Our Marketing department can assist with content strategy, campaign analysis, and lead generation. Would you like me to connect you with specific marketing insights?"

        if any(word in message_lower for word in ["product", "development", "engineering"]):
            return "The Product & Engineering team can help with technical roadmaps, development priorities, and project status. What aspect of product development interests you?"

        if any(word in message_lower for word in ["help", "what can you do"]):
            return "I'm your Executive AI Assistant. I can help with: strategic discussions, department coordination, business analysis, and decision support. Our framework includes specialized agents for Sales, Marketing, Product, Customer Success, Operations, and Security."

        return f"Thank you for your query about '{message[:50]}...'. As your Executive AI Assistant, I'm here to help coordinate across departments and provide strategic insights. Could you provide more details about what you'd like to explore?"

    def analyze_business_request(self, request: str) -> Dict[str, Any]:
        """
        Analyze a business request and provide structured insights.

        Args:
            request: The business request to analyze

        Returns:
            Structured analysis with recommendations
        """
        # Determine which departments are involved
        departments = []
        request_lower = request.lower()

        if any(word in request_lower for word in ["sales", "lead", "revenue", "deal"]):
            departments.append("Sales")
        if any(word in request_lower for word in ["marketing", "content", "campaign", "brand"]):
            departments.append("Marketing")
        if any(word in request_lower for word in ["product", "feature", "development", "code"]):
            departments.append("Product")
        if any(word in request_lower for word in ["customer", "support", "success"]):
            departments.append("Customer Success")
        if any(word in request_lower for word in ["finance", "budget", "cost"]):
            departments.append("Operations")
        if any(word in request_lower for word in ["security", "compliance", "risk"]):
            departments.append("Security")

        if not departments:
            departments = ["General"]

        return {
            "request": request,
            "departments_involved": departments,
            "priority": "medium",
            "recommended_actions": [
                f"Consult with {departments[0]} department head",
                "Gather relevant data and metrics",
                "Schedule strategic review meeting"
            ],
            "estimated_complexity": "moderate",
            "timestamp": datetime.now().isoformat()
        }

    def reset_conversation(self, session_id: str = DEFAULT_SESSION) -> None:
        """Reset one session's conversation history and context"""
        with self._lock:
            self._sessions.pop(session_id, None)

    def get_conversation_history(self, session_id: str = DEFAULT_SESSION) -> List[Dict[str, str]]:
        """Get one session's conversation history"""
        with self._lock:
            session = self._sessions.get(session_id)
            return list(session["history"]) if session else []
