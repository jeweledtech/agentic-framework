"""
Sales Department Agents

This module provides specialized agents for sales operations including
lead processing, qualification, outreach, and CRM integration via n8n.
"""

from typing import Dict, Any, Optional, List
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools


class SalesLeadAgent(BaseAgent):
    """
    Agent for processing and qualifying sales leads.

    Capabilities:
    - Lead qualification against ICP criteria
    - Lead scoring and prioritization
    - CRM integration via n8n workflows
    - Intelligent lead routing
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the sales lead agent"""
        if config is None:
            config = AgentConfig(
                id="sales_lead_agent",
                role=AgentRole(
                    name="Sales Lead Specialist",
                    description="Expert in lead qualification, ICP matching, and sales prioritization",
                    goal="Qualify leads accurately and route them to appropriate sales workflows",
                    backstory=(
                        "You are an experienced sales professional with deep expertise in "
                        "identifying high-quality leads. You understand ICP criteria, buying signals, "
                        "and how to prioritize leads for maximum conversion rates."
                    )
                ),
                tools=AgentTools(
                    tool_names=[
                        "sales_kb_tool",
                        "n8n_sales_automation_tool",
                        "mcp_notion_crm_tool",
                        "web_search_tool"
                    ]
                ),
                department="sales",
                temperature=0.4
            )

        super().__init__(config)

    def process_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a new lead and provide initial analysis.

        Args:
            lead_data: Dictionary containing lead information

        Returns:
            Processed lead data with analysis and recommendations
        """
        task_description = f"""
        Process this new sales lead and provide a comprehensive analysis:

        Lead Information:
        - Name: {lead_data.get('name', 'Unknown')}
        - Email: {lead_data.get('email', 'Unknown')}
        - Company: {lead_data.get('company', 'Unknown')}
        - Source: {lead_data.get('source', 'Unknown')}
        - Additional Data: {lead_data.get('additional_data', {})}

        Please provide:
        1. Initial lead quality assessment (1-100 score)
        2. Company research summary
        3. Potential pain points and needs
        4. Recommended approach and talking points
        5. Priority level (Hot/Warm/Cold)
        6. Suggested next steps
        """

        expected_output = """
        Structured lead analysis report with:
        - Quality score and reasoning
        - Company insights
        - Recommended sales approach
        - Next action items
        """

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "lead": lead_data,
            "analysis": results[0] if results else "Analysis pending",
            "status": "processed"
        }

    def qualify_lead(
        self,
        lead_data: Dict[str, Any],
        icp_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Qualify a lead against ICP criteria.

        Args:
            lead_data: Lead information
            icp_criteria: Ideal Customer Profile criteria

        Returns:
            Qualification results with match score
        """
        default_icp = {
            "company_size": "50-500 employees",
            "industries": ["technology", "finance", "healthcare", "manufacturing"],
            "budget_range": "$10k-$100k annually",
            "decision_timeline": "1-6 months",
            "pain_points": ["efficiency", "automation", "scalability"]
        }

        icp = icp_criteria or default_icp

        task_description = f"""
        Qualify this lead against our Ideal Customer Profile (ICP):

        Lead Data:
        {lead_data}

        ICP Criteria:
        {icp}

        Provide:
        1. Overall ICP match score (0-100)
        2. Matching criteria (what aligns)
        3. Gap analysis (what doesn't align)
        4. Risk factors
        5. Recommendation (Pursue/Nurture/Disqualify)
        """

        expected_output = "Detailed ICP qualification report with actionable recommendations"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "lead_data": lead_data,
            "icp_criteria": icp,
            "qualification": results[0] if results else "Qualification pending",
            "status": "qualified"
        }

    def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate a numerical score for lead prioritization.

        Args:
            lead_data: Lead information

        Returns:
            Lead score with breakdown
        """
        task_description = f"""
        Calculate a comprehensive lead score for:

        {lead_data}

        Scoring dimensions (0-100 each):
        1. Fit Score: How well do they match our ICP?
        2. Intent Score: How ready are they to buy?
        3. Engagement Score: How engaged have they been?
        4. Authority Score: Do they have decision-making power?

        Provide weighted total score and priority tier.
        """

        expected_output = "Numerical lead score with dimensional breakdown"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "lead_data": lead_data,
            "score_analysis": results[0] if results else "Scoring pending",
            "status": "scored"
        }


class OutreachAgent(BaseAgent):
    """
    Agent for sales outreach and follow-up sequences.

    Capabilities:
    - Personalized email generation
    - Follow-up sequence management
    - Engagement tracking
    - n8n workflow triggers for automation
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the outreach agent"""
        if config is None:
            config = AgentConfig(
                id="outreach_agent",
                role=AgentRole(
                    name="Sales Outreach Specialist",
                    description="Expert in personalized outreach and sales communication",
                    goal="Create compelling, personalized outreach that converts leads",
                    backstory=(
                        "You are a master of sales communication with years of experience "
                        "crafting messages that resonate with prospects. You understand timing, "
                        "personalization, and the art of the follow-up."
                    )
                ),
                tools=AgentTools(
                    tool_names=[
                        "sales_kb_tool",
                        "n8n_sales_automation_tool",
                        "mcp_gmail_send_tool",
                        "web_search_tool"
                    ]
                ),
                department="sales",
                temperature=0.7
            )

        super().__init__(config)

    def create_outreach_email(
        self,
        lead_data: Dict[str, Any],
        email_type: str = "initial",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a personalized outreach email.

        Args:
            lead_data: Lead information
            email_type: Type of email (initial, follow_up, demo_request, etc.)
            context: Additional context for personalization

        Returns:
            Generated email content
        """
        task_description = f"""
        Create a personalized {email_type} sales email for:

        Lead: {lead_data.get('name', 'Unknown')}
        Company: {lead_data.get('company', 'Unknown')}
        Role: {lead_data.get('role', 'Unknown')}

        Additional Context: {context or 'None provided'}

        Requirements:
        1. Personalize based on company/industry research
        2. Reference relevant pain points
        3. Include clear value proposition
        4. Have a specific, low-friction CTA
        5. Keep it concise (under 150 words)
        6. Professional but warm tone
        """

        expected_output = """
        Email with:
        - Subject line
        - Email body
        - Suggested follow-up timing
        """

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "lead": lead_data,
            "email_type": email_type,
            "email_content": results[0] if results else "Email generation pending",
            "status": "generated"
        }

    def create_follow_up_sequence(
        self,
        lead_data: Dict[str, Any],
        num_emails: int = 4
    ) -> Dict[str, Any]:
        """
        Create a complete follow-up email sequence.

        Args:
            lead_data: Lead information
            num_emails: Number of emails in sequence

        Returns:
            Complete email sequence
        """
        task_description = f"""
        Create a {num_emails}-email follow-up sequence for:

        Lead: {lead_data}

        Guidelines:
        1. Each email should have a different angle/value prop
        2. Increase urgency subtly over the sequence
        3. Include timing recommendations between emails
        4. Vary CTA types (reply, call, demo, content)
        5. Plan for breakup email as final touch
        """

        expected_output = f"Complete {num_emails}-email sequence with timing"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "lead": lead_data,
            "sequence_length": num_emails,
            "sequence": results[0] if results else "Sequence generation pending",
            "status": "created"
        }

    def analyze_engagement(
        self,
        lead_id: str,
        engagement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze engagement patterns and recommend next actions.

        Args:
            lead_id: Lead identifier
            engagement_data: Engagement history (opens, clicks, replies)

        Returns:
            Engagement analysis with recommendations
        """
        task_description = f"""
        Analyze engagement for lead {lead_id}:

        Engagement Data:
        {engagement_data}

        Provide:
        1. Engagement score (0-100)
        2. Behavioral insights
        3. Best time/day to reach out
        4. Content preferences (inferred)
        5. Recommended next action
        6. Risk of going cold
        """

        expected_output = "Engagement analysis with specific next-step recommendations"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "lead_id": lead_id,
            "engagement_data": engagement_data,
            "analysis": results[0] if results else "Analysis pending",
            "status": "analyzed"
        }


# Export all agents
__all__ = ["SalesLeadAgent", "OutreachAgent"]
