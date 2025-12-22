"""
Enhanced inter-agent communication with standardized message format
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json

class AgentCommunicationProtocol:
    """Enhanced inter-agent communication with standardized message format"""
    
    @staticmethod
    def create_delegation_message(sender_id: str, recipient_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized delegation message"""
        return {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "sender": {
                "agent_id": sender_id,
                "authority_level": task.get("sender_authority", "L2")
            },
            "recipient": {
                "agent_id": recipient_id,
                "required_response_time": task.get("response_time", "60 minutes")
            },
            "message_type": "REQUEST",
            "priority": task.get("priority", "MEDIUM"),
            "business_context": {
                "objective": task.get("objective"),
                "deadline": task.get("deadline"),
                "stakeholders": task.get("stakeholders", [])
            },
            "payload": {
                "task_description": task["description"],
                "data_requirements": task.get("data_requirements", []),
                "tool_recommendations": task.get("recommended_tools", []),
                "success_criteria": task.get("success_criteria", []),
                "constraints": task.get("constraints", [])
            },
            "thread_id": task.get("thread_id", str(uuid.uuid4()))
        }
    
    @staticmethod
    def create_response_message(original_message: Dict[str, Any], sender_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized response message"""
        return {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "sender": {
                "agent_id": sender_id,
                "response_to": original_message["message_id"]
            },
            "recipient": {
                "agent_id": original_message["sender"]["agent_id"]
            },
            "message_type": "RESPONSE",
            "priority": original_message.get("priority", "MEDIUM"),
            "thread_id": original_message.get("thread_id"),
            "payload": {
                "status": result.get("status", "COMPLETED"),
                "executive_summary": result.get("executive_summary", ""),
                "detailed_results": result.get("detailed_results", {}),
                "recommendations": result.get("recommendations", []),
                "confidence_level": result.get("confidence_level", "MEDIUM"),
                "escalation_needs": result.get("escalation_needs", []),
                "quality_metrics": result.get("quality_metrics", {}),
                "next_steps": result.get("next_steps", [])
            }
        }
    
    @staticmethod
    def create_escalation_message(sender_id: str, recipient_id: str, escalation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create escalation message for complex issues"""
        return {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "sender": {
                "agent_id": sender_id,
                "authority_level": escalation_context.get("sender_authority", "L1")
            },
            "recipient": {
                "agent_id": recipient_id,
                "required_response_time": "30 minutes"  # Escalations need faster response
            },
            "message_type": "ESCALATION",
            "priority": "HIGH",
            "business_context": {
                "escalation_reason": escalation_context.get("reason", "Complex issue requiring higher authority"),
                "original_task": escalation_context.get("original_task", {}),
                "blocking_factors": escalation_context.get("blocking_factors", []),
                "business_impact": escalation_context.get("business_impact", "MEDIUM")
            },
            "payload": {
                "issue_description": escalation_context["issue_description"],
                "attempted_solutions": escalation_context.get("attempted_solutions", []),
                "resource_needs": escalation_context.get("resource_needs", []),
                "recommended_action": escalation_context.get("recommended_action", ""),
                "timeline_impact": escalation_context.get("timeline_impact", "")
            },
            "thread_id": escalation_context.get("thread_id", str(uuid.uuid4()))
        }
    
    @staticmethod
    def create_handoff_template(task_context: Dict[str, Any]) -> str:
        """Generate handoff template for agent delegation"""
        return f"""
You are receiving a task handoff from {task_context.get('sender_agent', 'Unknown Agent')}. 

HANDOFF CONTEXT:
- Original Request: {task_context.get('original_task', 'Not specified')}
- Your Role: {task_context.get('recipient_responsibility', 'Not specified')}
- Expected Deliverable: {task_context.get('expected_output', 'Not specified')}
- Deadline: {task_context.get('deadline', 'Not specified')}
- Quality Standards: {task_context.get('success_criteria', 'Standard quality expected')}

AVAILABLE RESOURCES:
- Data Sources: {task_context.get('data_sources', 'To be determined')}
- Tools: {task_context.get('available_tools', 'Standard agent tools')}
- Support Agents: {task_context.get('collaboration_options', 'None specified')}

HANDOFF REQUIREMENTS:
When complete, provide your output in this format:
1. Executive Summary (3 bullet points max)
2. Detailed Results (structured data/analysis)
3. Recommendations (actionable next steps)
4. Confidence Level (High/Medium/Low with reasoning)
5. Escalation Needs (if any)

QUALITY ASSURANCE:
Before responding, verify:
- ✓ Output meets all specified criteria
- ✓ Data sources are properly cited
- ✓ Recommendations are actionable
- ✓ Any risks or limitations are noted

BUSINESS CONTEXT:
- Department: {task_context.get('department', 'Cross-functional')}
- Stakeholders: {task_context.get('stakeholders', 'Executive team')}
- Success Metrics: {task_context.get('success_metrics', 'Standard KPIs')}
- Risk Tolerance: {task_context.get('risk_tolerance', 'Standard')}
"""

    @staticmethod
    def create_collaboration_request(initiator_id: str, collaborators: List[str], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create collaboration request for multi-agent projects"""
        return {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "initiator": {
                "agent_id": initiator_id,
                "role": project_context.get("initiator_role", "Project Lead")
            },
            "collaborators": [
                {
                    "agent_id": collaborator,
                    "expected_contribution": project_context.get("contributions", {}).get(collaborator, "TBD")
                }
                for collaborator in collaborators
            ],
            "message_type": "COLLABORATION_REQUEST",
            "priority": project_context.get("priority", "MEDIUM"),
            "project_context": {
                "project_name": project_context.get("project_name", "Cross-functional Project"),
                "objective": project_context.get("objective", ""),
                "timeline": project_context.get("timeline", "TBD"),
                "deliverables": project_context.get("deliverables", []),
                "success_criteria": project_context.get("success_criteria", [])
            },
            "coordination_plan": {
                "meeting_schedule": project_context.get("meeting_schedule", "Weekly"),
                "communication_channels": project_context.get("communication_channels", ["agent_messaging"]),
                "milestone_reviews": project_context.get("milestones", []),
                "reporting_structure": project_context.get("reporting", "Initiator consolidates updates")
            },
            "thread_id": str(uuid.uuid4())
        }

class MessageRouter:
    """Route messages between agents based on department hierarchy and authority levels"""
    
    def __init__(self):
        self.message_history = []
        self.active_threads = {}
        
    def route_message(self, message: Dict[str, Any], department_hierarchy: Dict[str, Any]) -> List[str]:
        """Route message to appropriate recipients"""
        
        # Store message in history
        self.message_history.append(message)
        
        # Update active threads
        thread_id = message.get("thread_id")
        if thread_id:
            if thread_id not in self.active_threads:
                self.active_threads[thread_id] = []
            self.active_threads[thread_id].append(message)
        
        # Determine routing based on message type and hierarchy
        recipients = []
        
        if message["message_type"] == "ESCALATION":
            recipients = self._route_escalation(message, department_hierarchy)
        elif message["message_type"] == "COLLABORATION_REQUEST":
            recipients = self._route_collaboration(message, department_hierarchy)
        elif message["message_type"] == "REQUEST":
            recipients = self._route_request(message, department_hierarchy)
        elif message["message_type"] == "RESPONSE":
            recipients = self._route_response(message, department_hierarchy)
        
        return recipients
    
    def _route_escalation(self, message: Dict[str, Any], hierarchy: Dict[str, Any]) -> List[str]:
        """Route escalation message up the hierarchy"""
        sender_id = message["sender"]["agent_id"]
        
        # Find sender's department and escalate to department head
        for dept, agents in hierarchy.items():
            if sender_id in agents.get("managers", []):
                return [agents.get("head", "")]
            elif sender_id == agents.get("head", ""):
                # Department head escalating to chief
                return ["chief_agent"]
        
        return ["chief_agent"]  # Default escalation
    
    def _route_collaboration(self, message: Dict[str, Any], hierarchy: Dict[str, Any]) -> List[str]:
        """Route collaboration request to specified collaborators"""
        return [collaborator["agent_id"] for collaborator in message.get("collaborators", [])]
    
    def _route_request(self, message: Dict[str, Any], hierarchy: Dict[str, Any]) -> List[str]:
        """Route request message to specified recipient"""
        return [message["recipient"]["agent_id"]]
    
    def _route_response(self, message: Dict[str, Any], hierarchy: Dict[str, Any]) -> List[str]:
        """Route response message back to original sender"""
        return [message["recipient"]["agent_id"]]

class CommunicationAnalytics:
    """Analyze communication patterns and effectiveness"""
    
    def __init__(self):
        self.communication_metrics = {
            "message_volume": {},
            "response_times": {},
            "collaboration_patterns": {},
            "escalation_frequency": {}
        }
    
    def analyze_communication_patterns(self, message_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze communication patterns from message history"""
        
        analysis = {
            "total_messages": len(message_history),
            "message_types": self._analyze_message_types(message_history),
            "average_response_time": self._calculate_average_response_time(message_history),
            "escalation_rate": self._calculate_escalation_rate(message_history),
            "collaboration_effectiveness": self._assess_collaboration_effectiveness(message_history),
            "communication_quality": self._assess_communication_quality(message_history)
        }
        
        return analysis
    
    def _analyze_message_types(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of message types"""
        type_counts = {}
        for message in messages:
            msg_type = message.get("message_type", "UNKNOWN")
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        return type_counts
    
    def _calculate_average_response_time(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate average response time for requests"""
        response_times = []
        
        # Group messages by thread to calculate response times
        threads = {}
        for message in messages:
            thread_id = message.get("thread_id")
            if thread_id:
                if thread_id not in threads:
                    threads[thread_id] = []
                threads[thread_id].append(message)
        
        # Calculate response times for each thread
        for thread_messages in threads.values():
            requests = [msg for msg in thread_messages if msg.get("message_type") == "REQUEST"]
            responses = [msg for msg in thread_messages if msg.get("message_type") == "RESPONSE"]
            
            for request in requests:
                for response in responses:
                    if response.get("sender", {}).get("response_to") == request.get("message_id"):
                        # Calculate time difference (simplified - would use actual timestamp parsing)
                        response_times.append(60)  # Mock: 60 minutes average
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _calculate_escalation_rate(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate rate of escalations"""
        total_requests = len([msg for msg in messages if msg.get("message_type") == "REQUEST"])
        escalations = len([msg for msg in messages if msg.get("message_type") == "ESCALATION"])
        
        return escalations / total_requests if total_requests > 0 else 0
    
    def _assess_collaboration_effectiveness(self, messages: List[Dict[str, Any]]) -> float:
        """Assess effectiveness of collaborative communications"""
        collaborations = [msg for msg in messages if msg.get("message_type") == "COLLABORATION_REQUEST"]
        
        if not collaborations:
            return 1.0
        
        # Mock assessment - would analyze actual collaboration outcomes
        return 0.85
    
    def _assess_communication_quality(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Assess overall communication quality metrics"""
        return {
            "clarity_score": 0.88,  # Mock scores - would analyze actual message content
            "completeness_score": 0.92,
            "timeliness_score": 0.85,
            "professionalism_score": 0.95
        }