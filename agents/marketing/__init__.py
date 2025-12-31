"""
Marketing Department Agents

This module provides specialized agents for marketing operations including
content creation, campaign management, and analytics via n8n integration.
"""

from typing import Dict, Any, Optional, List
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools


class ContentMarketingAgent(BaseAgent):
    """
    Agent for content creation and distribution.

    Capabilities:
    - Blog post generation
    - Social media content
    - Email campaign content
    - SEO optimization
    - n8n workflow triggers for distribution
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the content marketing agent"""
        if config is None:
            config = AgentConfig(
                id="content_marketing_agent",
                role=AgentRole(
                    name="Content Marketing Specialist",
                    description="Expert in creating compelling marketing content across channels",
                    goal="Create high-quality, engaging content that drives conversions",
                    backstory=(
                        "You are a seasoned content marketer with expertise in B2B and B2C "
                        "content strategy. You understand SEO, buyer psychology, and how to "
                        "craft messages that resonate with target audiences."
                    )
                ),
                tools=AgentTools(
                    tool_names=[
                        "marketing_kb_tool",
                        "n8n_marketing_automation_tool",
                        "mcp_content_storage_tool",
                        "web_search_tool"
                    ]
                ),
                department="marketing",
                temperature=0.8  # Higher creativity for content
            )

        super().__init__(config)

    def create_blog_post(
        self,
        topic: str,
        target_audience: str = "general",
        word_count: int = 1200,
        seo_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete blog post.

        Args:
            topic: Blog post topic
            target_audience: Target reader persona
            word_count: Approximate word count
            seo_keywords: Keywords to optimize for

        Returns:
            Complete blog post with metadata
        """
        keywords_str = ", ".join(seo_keywords) if seo_keywords else "to be determined"

        task_description = f"""
        Create a comprehensive blog post on: {topic}

        Requirements:
        - Target Audience: {target_audience}
        - Word Count: ~{word_count} words
        - SEO Keywords: {keywords_str}

        Include:
        1. Compelling headline (with alternatives)
        2. Meta description (150-160 chars)
        3. Introduction with hook
        4. Structured body with H2/H3 headers
        5. Actionable takeaways
        6. Strong CTA
        7. Internal/external link suggestions
        """

        expected_output = """
        Complete blog post with:
        - Headlines (primary + alternatives)
        - Meta description
        - Full article content
        - SEO recommendations
        """

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "topic": topic,
            "target_audience": target_audience,
            "word_count": word_count,
            "content": results[0] if results else "Content generation pending",
            "status": "created"
        }

    def create_social_content(
        self,
        topic: str,
        platforms: List[str] = None,
        campaign_theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create social media content for multiple platforms.

        Args:
            topic: Content topic
            platforms: Target platforms (LinkedIn, Twitter, etc.)
            campaign_theme: Optional campaign theme

        Returns:
            Platform-specific social content
        """
        platforms = platforms or ["LinkedIn", "Twitter", "Facebook"]

        task_description = f"""
        Create social media content about: {topic}

        Platforms: {', '.join(platforms)}
        Campaign Theme: {campaign_theme or 'General awareness'}

        For each platform provide:
        1. Platform-optimized copy (right length/format)
        2. Hashtag suggestions
        3. Best posting time recommendation
        4. Visual content suggestions
        5. Engagement hook/question
        """

        expected_output = "Platform-specific social media content package"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "topic": topic,
            "platforms": platforms,
            "campaign_theme": campaign_theme,
            "content": results[0] if results else "Content generation pending",
            "status": "created"
        }

    def create_email_campaign(
        self,
        campaign_name: str,
        campaign_goal: str,
        num_emails: int = 3,
        target_segment: str = "all subscribers"
    ) -> Dict[str, Any]:
        """
        Create an email marketing campaign.

        Args:
            campaign_name: Name of the campaign
            campaign_goal: Primary campaign objective
            num_emails: Number of emails in the sequence
            target_segment: Target audience segment

        Returns:
            Complete email campaign
        """
        task_description = f"""
        Create a {num_emails}-email marketing campaign:

        Campaign: {campaign_name}
        Goal: {campaign_goal}
        Target Segment: {target_segment}

        For each email provide:
        1. Subject line (with A/B variants)
        2. Preview text
        3. Email body (HTML-ready)
        4. CTA button text
        5. Sending timing recommendation
        6. A/B test suggestions
        """

        expected_output = "Complete email campaign with all emails and timing"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "campaign_name": campaign_name,
            "campaign_goal": campaign_goal,
            "num_emails": num_emails,
            "target_segment": target_segment,
            "campaign": results[0] if results else "Campaign generation pending",
            "status": "created"
        }


class CampaignAgent(BaseAgent):
    """
    Agent for campaign management and analytics.

    Capabilities:
    - Campaign performance analysis
    - A/B test recommendations
    - ROI calculations
    - Optimization suggestions
    - n8n workflow triggers for reporting
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the campaign agent"""
        if config is None:
            config = AgentConfig(
                id="campaign_agent",
                role=AgentRole(
                    name="Marketing Campaign Manager",
                    description="Expert in campaign strategy, analysis, and optimization",
                    goal="Maximize campaign ROI through data-driven optimization",
                    backstory=(
                        "You are a data-driven marketing strategist with deep experience "
                        "in multi-channel campaigns. You excel at interpreting metrics, "
                        "identifying optimization opportunities, and driving measurable results."
                    )
                ),
                tools=AgentTools(
                    tool_names=[
                        "marketing_kb_tool",
                        "n8n_marketing_automation_tool",
                        "mcp_analytics_api_tool",
                        "web_search_tool"
                    ]
                ),
                department="marketing",
                temperature=0.5
            )

        super().__init__(config)

    def analyze_campaign(
        self,
        campaign_id: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze campaign performance.

        Args:
            campaign_id: Campaign identifier
            metrics: Campaign performance metrics

        Returns:
            Detailed analysis with recommendations
        """
        task_description = f"""
        Analyze campaign performance for: {campaign_id}

        Metrics:
        {metrics}

        Provide:
        1. Performance summary (vs benchmarks)
        2. Key insights (what's working/not working)
        3. Audience insights
        4. Channel performance breakdown
        5. Cost efficiency analysis
        6. Specific optimization recommendations
        7. A/B test priorities
        """

        expected_output = "Comprehensive campaign analysis with actionable insights"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "campaign_id": campaign_id,
            "metrics": metrics,
            "analysis": results[0] if results else "Analysis pending",
            "status": "analyzed"
        }

    def calculate_roi(
        self,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate campaign ROI and unit economics.

        Args:
            campaign_data: Campaign cost and revenue data

        Returns:
            ROI analysis
        """
        task_description = f"""
        Calculate ROI for campaign:

        {campaign_data}

        Provide:
        1. Overall ROI percentage
        2. Cost per acquisition (CPA)
        3. Customer lifetime value impact
        4. Channel-specific ROI
        5. Comparison to benchmarks
        6. Break-even analysis
        7. Recommendations for improvement
        """

        expected_output = "Detailed ROI analysis with financial breakdown"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "campaign_data": campaign_data,
            "roi_analysis": results[0] if results else "ROI calculation pending",
            "status": "calculated"
        }

    def create_campaign_plan(
        self,
        campaign_objective: str,
        budget: float,
        duration_weeks: int = 4,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive campaign plan.

        Args:
            campaign_objective: Primary campaign goal
            budget: Available budget
            duration_weeks: Campaign duration
            channels: Marketing channels to use

        Returns:
            Complete campaign plan
        """
        channels = channels or ["Email", "Social Media", "Content", "Paid Ads"]

        task_description = f"""
        Create a marketing campaign plan:

        Objective: {campaign_objective}
        Budget: ${budget:,.2f}
        Duration: {duration_weeks} weeks
        Channels: {', '.join(channels)}

        Include:
        1. Campaign strategy overview
        2. Target audience definition
        3. Channel allocation (with budget split)
        4. Content calendar outline
        5. Key milestones and checkpoints
        6. Success metrics and KPIs
        7. Risk mitigation strategies
        8. Resource requirements
        """

        expected_output = "Comprehensive campaign plan ready for execution"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "objective": campaign_objective,
            "budget": budget,
            "duration_weeks": duration_weeks,
            "channels": channels,
            "plan": results[0] if results else "Plan generation pending",
            "status": "planned"
        }

    def suggest_optimizations(
        self,
        campaign_id: str,
        current_performance: Dict[str, Any],
        target_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest optimizations to improve campaign performance.

        Args:
            campaign_id: Campaign identifier
            current_performance: Current metrics
            target_metrics: Target metrics to achieve

        Returns:
            Optimization recommendations
        """
        task_description = f"""
        Suggest optimizations for campaign: {campaign_id}

        Current Performance:
        {current_performance}

        Target Metrics:
        {target_metrics}

        Provide prioritized recommendations for:
        1. Quick wins (implement immediately)
        2. Medium-term improvements
        3. Strategic changes
        4. A/B tests to run
        5. Budget reallocation suggestions
        6. Creative refresh ideas
        """

        expected_output = "Prioritized optimization roadmap"

        self.add_task(task_description, expected_output)
        results = self.execute_tasks()

        return {
            "campaign_id": campaign_id,
            "current_performance": current_performance,
            "target_metrics": target_metrics,
            "optimizations": results[0] if results else "Optimization analysis pending",
            "status": "recommended"
        }


# Export all agents
__all__ = ["ContentMarketingAgent", "CampaignAgent"]
