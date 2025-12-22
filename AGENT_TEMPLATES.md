# Agent Templates

**Ready-to-use templates for building your 58-agent workforce**

This document provides copy-paste templates for implementing agents across all 6 departments. Each template follows the framework's patterns and can be customized for your specific business needs.

---

## Table of Contents

1. [Department Overview](#department-overview)
2. [Sales & Lead Management (10 Agents)](#sales--lead-management)
3. [Marketing & Content Creation (8 Agents)](#marketing--content-creation)
4. [Product Development & Code (12 Agents)](#product-development--code)
5. [Customer Success & Support (9 Agents)](#customer-success--support)
6. [Operations & Back Office (6 Agents)](#operations--back-office)
7. [Security & Compliance (13 Agents)](#security--compliance)
8. [Chief Agent](#chief-agent)
9. [Agent Communication Patterns](#agent-communication-patterns)

---

## Department Overview

| Department | Agents | Department Head | Primary Focus |
|------------|--------|-----------------|---------------|
| Sales | 10 | Head of Sales | Revenue generation, lead management |
| Marketing | 8 | Head of Marketing | Content, campaigns, brand awareness |
| Product | 12 | Head of Engineering | Development, testing, deployment |
| Customer Success | 9 | Customer Success Manager | Onboarding, support, retention |
| Operations | 6 | Head of Operations | Finance, HR, administration |
| Security | 13 | Chief Security Officer | Compliance, security, risk |

**Total: 58 specialized agents**

---

## Sales & Lead Management

### Directory Structure

```
agents/sales/
├── __init__.py
├── head_of_sales.py
├── outbound/
│   ├── __init__.py
│   ├── manager.py
│   ├── lead_gen.py
│   ├── email_outreach.py
│   ├── cold_calling.py
│   └── crm_update.py
└── inbound/
    ├── __init__.py
    ├── manager.py
    ├── lead_qualification.py
    ├── demo_scheduler.py
    └── proposal_writer.py
```

### 1. Head of Sales Agent

```python
"""
agents/sales/head_of_sales.py
Department head for all sales operations.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class HeadOfSalesAgent(BaseAgent):
    """
    Head of Sales - Coordinates all sales activities.
    Reports to: Chief Agent
    Manages: Outbound Manager, Inbound Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="HeadOfSales",
            role=AgentRole(
                name="Head of Sales",
                goal="""Drive revenue growth through strategic sales leadership,
                pipeline optimization, and team coordination. Ensure both
                outbound and inbound channels are operating at peak efficiency.""",
                backstory="""You are a veteran sales leader with 15+ years of
                experience building high-performing sales organizations. You've
                led teams from startup to enterprise scale, and you understand
                both the art and science of sales. You excel at forecasting,
                strategy development, and coaching sales talent. You believe
                in data-driven decision making and customer-centric selling."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.6,
            verbose=True
        )
        super().__init__(config)

    def analyze_pipeline(self, pipeline_data: dict) -> dict:
        """Analyze sales pipeline health and opportunities."""
        self.add_task(
            description=f"""Analyze this sales pipeline:
            {pipeline_data}

            Provide:
            1. Pipeline health score (1-100)
            2. Stage conversion analysis
            3. At-risk deals
            4. Revenue forecast
            5. Recommended actions""",
            expected_output="Comprehensive pipeline analysis with actionable recommendations"
        )
        results = self.execute_tasks()
        return {"analysis": results[0] if results else "Analysis unavailable"}

    def create_sales_strategy(self, quarter: str, targets: dict) -> str:
        """Create quarterly sales strategy."""
        self.add_task(
            description=f"""Create a comprehensive sales strategy for {quarter}:
            Targets: {targets}

            Include:
            1. Revenue targets breakdown
            2. Outbound vs inbound allocation
            3. Key initiatives
            4. Team assignments
            5. Risk mitigation plans""",
            expected_output="Detailed quarterly sales strategy document"
        )
        results = self.execute_tasks()
        return results[0] if results else "Strategy generation failed"

    def delegate_lead(self, lead: dict) -> dict:
        """Route lead to appropriate team."""
        source = lead.get("source", "").lower()

        if source in ["website", "referral", "demo_request", "inbound_call"]:
            return {
                "team": "inbound",
                "agent": "InboundManager",
                "priority": self._calculate_priority(lead)
            }
        else:
            return {
                "team": "outbound",
                "agent": "OutboundManager",
                "priority": self._calculate_priority(lead)
            }

    def _calculate_priority(self, lead: dict) -> str:
        """Calculate lead priority based on signals."""
        score = 0
        if lead.get("company_size", 0) > 100:
            score += 3
        if lead.get("budget_mentioned"):
            score += 3
        if lead.get("timeline", "").lower() in ["immediate", "this_quarter"]:
            score += 4

        if score >= 7:
            return "high"
        elif score >= 4:
            return "medium"
        return "low"
```

### 2. Outbound Sales Manager

```python
"""
agents/sales/outbound/manager.py
Manages outbound sales team.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class OutboundSalesManager(BaseAgent):
    """
    Outbound Sales Manager - Leads prospecting and outreach efforts.
    Reports to: Head of Sales
    Manages: Lead Gen, Email Outreach, Cold Calling, CRM Update agents
    """

    def __init__(self):
        config = AgentConfig(
            name="OutboundSalesManager",
            role=AgentRole(
                name="Outbound Sales Manager",
                goal="""Build a predictable pipeline of qualified opportunities
                through strategic outbound prospecting. Optimize outreach
                sequences and maximize conversion rates.""",
                backstory="""You are an expert in outbound sales methodology
                with deep experience in B2B prospecting. You've mastered
                multi-channel outreach, understand buyer psychology, and
                know how to craft compelling messages that get responses.
                You believe in quality over quantity and personalization
                at scale."""
            ),
            tool_names=[
                "knowledge_base_query",
                "web_search",
                "file_write"
            ],
            temperature=0.5,
            verbose=True
        )
        super().__init__(config)

    def create_prospecting_plan(self, target_accounts: list) -> dict:
        """Create a prospecting plan for target accounts."""
        self.add_task(
            description=f"""Create a detailed prospecting plan for:
            {target_accounts}

            For each account, define:
            1. Key personas to target
            2. Outreach sequence (email, phone, LinkedIn)
            3. Value proposition to lead with
            4. Trigger events to monitor
            5. Success metrics""",
            expected_output="Account-based prospecting plan with sequences"
        )
        results = self.execute_tasks()
        return {"plan": results[0] if results else "Plan generation failed"}

    def assign_leads_to_team(self, leads: list) -> list:
        """Assign leads to appropriate team members."""
        assignments = []
        for lead in leads:
            assignment = {
                "lead": lead,
                "assigned_to": self._select_agent(lead),
                "priority": lead.get("priority", "medium"),
                "action": self._determine_action(lead)
            }
            assignments.append(assignment)
        return assignments

    def _select_agent(self, lead: dict) -> str:
        """Select the right agent based on lead characteristics."""
        if not lead.get("email_found"):
            return "LeadGenerationAgent"
        if lead.get("cold_call_preferred"):
            return "ColdCallingAgent"
        return "EmailOutreachAgent"

    def _determine_action(self, lead: dict) -> str:
        """Determine next action for lead."""
        if not lead.get("researched"):
            return "research"
        if not lead.get("contacted"):
            return "initial_outreach"
        return "follow_up"
```

### 3. Lead Generation Agent

```python
"""
agents/sales/outbound/lead_gen.py
Identifies and researches potential leads.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class LeadGenerationAgent(BaseAgent):
    """
    Lead Generation Specialist - Finds and qualifies prospects.
    Reports to: Outbound Sales Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="LeadGenerationAgent",
            role=AgentRole(
                name="Lead Generation Specialist",
                goal="""Identify high-quality leads matching our ideal customer
                profile. Research companies thoroughly to enable personalized
                outreach and higher conversion rates.""",
                backstory="""You are a skilled researcher and prospector who
                excels at finding the right people at the right companies.
                You understand how to use various data sources to build
                comprehensive prospect profiles. You can identify pain points
                and triggers that signal buying intent."""
            ),
            tool_names=[
                "web_search",
                "knowledge_base_query",
                "file_write"
            ],
            temperature=0.4,
            verbose=True
        )
        super().__init__(config)

    def find_prospects(self, criteria: dict) -> list:
        """Find prospects matching criteria."""
        self.add_task(
            description=f"""Research and identify potential prospects:

            Criteria:
            - Industry: {criteria.get('industry', 'Any')}
            - Company size: {criteria.get('size', '50-500')}
            - Location: {criteria.get('location', 'US')}
            - Technologies: {criteria.get('technologies', 'Any')}

            For each prospect, provide:
            1. Company name and overview
            2. Why they're a good fit
            3. Key decision makers
            4. Potential pain points
            5. Recent news or triggers""",
            expected_output="List of 10 qualified prospects with research"
        )
        results = self.execute_tasks()
        return results

    def enrich_lead(self, company_name: str) -> dict:
        """Enrich a lead with additional data."""
        self.add_task(
            description=f"""Research {company_name} thoroughly:

            Find:
            1. Company overview and mission
            2. Recent news and announcements
            3. Technology stack
            4. Key executives and their backgrounds
            5. Potential pain points we can address
            6. Competitors they might be working with
            7. Best angle for outreach""",
            expected_output="Comprehensive company profile"
        )
        results = self.execute_tasks()
        return {
            "company": company_name,
            "research": results[0] if results else "Research unavailable"
        }
```

### 4. Email Outreach Agent

```python
"""
agents/sales/outbound/email_outreach.py
Crafts and manages email campaigns.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class EmailOutreachAgent(BaseAgent):
    """
    Email Outreach Specialist - Creates personalized email sequences.
    Reports to: Outbound Sales Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="EmailOutreachAgent",
            role=AgentRole(
                name="Email Outreach Specialist",
                goal="""Create highly personalized, compelling email sequences
                that generate responses and book meetings. Optimize subject
                lines, messaging, and timing for maximum effectiveness.""",
                backstory="""You are an expert copywriter specializing in B2B
                sales emails. You understand what makes decision-makers open
                and respond to cold emails. You craft messages that are
                personal, relevant, and value-driven. You avoid spam triggers
                and focus on building genuine connections."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.7,
            verbose=True
        )
        super().__init__(config)

    def create_email_sequence(self, prospect: dict, campaign_type: str) -> list:
        """Create a personalized email sequence."""
        self.add_task(
            description=f"""Create a 5-email sequence for:

            Prospect: {prospect}
            Campaign Type: {campaign_type}

            For each email, provide:
            1. Subject line (and 2 alternatives)
            2. Email body (personalized)
            3. Call to action
            4. Recommended send timing
            5. Follow-up trigger conditions

            Make emails:
            - Personal and specific to their situation
            - Value-focused, not product-focused
            - Conversational and human
            - Under 150 words each""",
            expected_output="5-email sequence with variations"
        )
        results = self.execute_tasks()
        return results

    def write_follow_up(self, context: dict) -> str:
        """Write a follow-up email based on context."""
        self.add_task(
            description=f"""Write a follow-up email:

            Previous interaction: {context.get('last_interaction', 'None')}
            Days since last contact: {context.get('days_since', 7)}
            Prospect response: {context.get('response', 'No response')}

            Create a follow-up that:
            1. References previous interaction naturally
            2. Adds new value or insight
            3. Has a clear, low-friction CTA
            4. Stays under 100 words""",
            expected_output="Follow-up email with subject line"
        )
        results = self.execute_tasks()
        return results[0] if results else "Email generation failed"
```

---

## Marketing & Content Creation

### Directory Structure

```
agents/marketing/
├── __init__.py
├── head_of_marketing.py
├── content/
│   ├── __init__.py
│   ├── manager.py
│   ├── blog_writer.py
│   ├── social_media.py
│   └── video_script.py
├── campaigns/
│   ├── __init__.py
│   ├── email_marketing.py
│   └── ads_manager.py
└── seo_specialist.py
```

### 5. Head of Marketing Agent

```python
"""
agents/marketing/head_of_marketing.py
Department head for all marketing operations.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class HeadOfMarketingAgent(BaseAgent):
    """
    Head of Marketing - Leads all marketing initiatives.
    Reports to: Chief Agent
    Manages: Content Manager, Campaign Manager, SEO Specialist
    """

    def __init__(self):
        config = AgentConfig(
            name="HeadOfMarketing",
            role=AgentRole(
                name="Head of Marketing",
                goal="""Build brand awareness, generate qualified leads, and
                support sales with compelling content and campaigns. Create
                a cohesive marketing strategy that drives measurable results.""",
                backstory="""You are a strategic marketing leader with
                expertise across digital marketing, content strategy, and
                brand building. You've scaled marketing operations for
                multiple successful companies. You believe in data-driven
                marketing and understand the full funnel from awareness
                to conversion."""
            ),
            tool_names=[
                "knowledge_base_query",
                "web_search",
                "file_write"
            ],
            temperature=0.6,
            verbose=True
        )
        super().__init__(config)

    def create_marketing_strategy(self, period: str, budget: float) -> dict:
        """Create comprehensive marketing strategy."""
        self.add_task(
            description=f"""Create a marketing strategy for {period}:
            Budget: ${budget:,.2f}

            Include:
            1. Goals and KPIs
            2. Target audience segments
            3. Channel strategy and budget allocation
            4. Content calendar themes
            5. Campaign initiatives
            6. Team assignments
            7. Measurement framework""",
            expected_output="Comprehensive marketing strategy document"
        )
        results = self.execute_tasks()
        return {"strategy": results[0] if results else "Strategy unavailable"}

    def analyze_marketing_performance(self, metrics: dict) -> dict:
        """Analyze marketing performance and provide recommendations."""
        self.add_task(
            description=f"""Analyze these marketing metrics:
            {metrics}

            Provide:
            1. Performance summary by channel
            2. ROI analysis
            3. What's working well
            4. Areas needing improvement
            5. Recommended optimizations
            6. Budget reallocation suggestions""",
            expected_output="Marketing performance analysis with recommendations"
        )
        results = self.execute_tasks()
        return {"analysis": results[0] if results else "Analysis unavailable"}
```

### 6. Content Manager Agent

```python
"""
agents/marketing/content/manager.py
Manages content strategy and production.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class ContentManagerAgent(BaseAgent):
    """
    Content Manager - Oversees all content creation.
    Reports to: Head of Marketing
    Manages: Blog Writer, Social Media, Video Script agents
    """

    def __init__(self):
        config = AgentConfig(
            name="ContentManager",
            role=AgentRole(
                name="Content Manager",
                goal="""Develop and execute a content strategy that educates,
                engages, and converts our target audience. Ensure consistent
                brand voice and quality across all content channels.""",
                backstory="""You are an experienced content strategist who
                understands how to create content that resonates with B2B
                audiences. You have expertise in content marketing, SEO,
                and editorial management. You balance creativity with
                strategic thinking to produce content that drives results."""
            ),
            tool_names=[
                "knowledge_base_query",
                "web_search",
                "file_write"
            ],
            temperature=0.7,
            verbose=True
        )
        super().__init__(config)

    def create_content_calendar(self, month: str, themes: list) -> dict:
        """Create monthly content calendar."""
        self.add_task(
            description=f"""Create a content calendar for {month}:
            Themes: {themes}

            Include for each week:
            1. Blog posts (2 per week)
            2. Social media posts (daily)
            3. Email newsletter content
            4. Video content ideas
            5. SEO keywords to target
            6. Content owner assignments""",
            expected_output="Complete content calendar with assignments"
        )
        results = self.execute_tasks()
        return {"calendar": results[0] if results else "Calendar unavailable"}

    def create_content_brief(self, topic: str, content_type: str) -> dict:
        """Create a detailed content brief."""
        self.add_task(
            description=f"""Create a content brief for:
            Topic: {topic}
            Type: {content_type}

            Include:
            1. Target audience and persona
            2. Goals and desired outcomes
            3. Key messages and talking points
            4. SEO keywords and search intent
            5. Outline/structure
            6. CTAs
            7. Reference materials
            8. Distribution plan""",
            expected_output="Detailed content brief"
        )
        results = self.execute_tasks()
        return {"brief": results[0] if results else "Brief unavailable"}
```

### 7. Blog Writer Agent

```python
"""
agents/marketing/content/blog_writer.py
Creates blog posts and long-form content.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class BlogWriterAgent(BaseAgent):
    """
    Blog Writer - Creates engaging blog content.
    Reports to: Content Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="BlogWriter",
            role=AgentRole(
                name="Blog Writer",
                goal="""Create informative, engaging, and SEO-optimized blog
                content that establishes thought leadership and drives
                organic traffic.""",
                backstory="""You are a skilled content writer with expertise
                in B2B technology topics. You can explain complex concepts
                clearly and create content that's both educational and
                engaging. You understand SEO best practices and how to
                structure content for readability and search performance."""
            ),
            tool_names=[
                "knowledge_base_query",
                "web_search",
                "file_write"
            ],
            temperature=0.8,
            verbose=True
        )
        super().__init__(config)

    def write_blog_post(self, brief: dict) -> str:
        """Write a complete blog post from brief."""
        self.add_task(
            description=f"""Write a blog post based on this brief:
            {brief}

            Requirements:
            1. Compelling headline with keyword
            2. Strong opening hook
            3. Well-structured with H2/H3 headings
            4. Include relevant examples
            5. Natural keyword integration
            6. Clear CTA
            7. Meta description
            8. Word count: {brief.get('word_count', 1500)}""",
            expected_output="Complete blog post in markdown format"
        )
        results = self.execute_tasks()
        return results[0] if results else "Blog post generation failed"

    def write_thought_leadership(self, topic: str, perspective: str) -> str:
        """Write thought leadership article."""
        self.add_task(
            description=f"""Write a thought leadership piece:
            Topic: {topic}
            Perspective: {perspective}

            Make it:
            1. Provocative yet professional
            2. Share unique insights
            3. Back up claims with reasoning
            4. Take a clear stance
            5. Provide actionable takeaways
            6. ~1200 words""",
            expected_output="Thought leadership article"
        )
        results = self.execute_tasks()
        return results[0] if results else "Article generation failed"
```

---

## Product Development & Code

### Directory Structure

```
agents/product/
├── __init__.py
├── head_of_engineering.py
├── frontend/
│   ├── __init__.py
│   ├── manager.py
│   ├── ui_developer.py
│   └── accessibility.py
├── backend/
│   ├── __init__.py
│   ├── manager.py
│   ├── api_developer.py
│   └── database.py
├── devops/
│   ├── __init__.py
│   ├── ci_cd.py
│   └── infrastructure.py
└── qa/
    ├── __init__.py
    ├── test_automation.py
    └── code_reviewer.py
```

### 8. Head of Engineering Agent

```python
"""
agents/product/head_of_engineering.py
Department head for product development.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class HeadOfEngineeringAgent(BaseAgent):
    """
    Head of Engineering - Leads technical development.
    Reports to: Chief Agent
    Manages: Frontend, Backend, DevOps, QA teams
    """

    def __init__(self):
        config = AgentConfig(
            name="HeadOfEngineering",
            role=AgentRole(
                name="Head of Engineering",
                goal="""Lead the technical organization to deliver high-quality
                software efficiently. Ensure technical excellence, team growth,
                and alignment between technical decisions and business goals.""",
                backstory="""You are a seasoned engineering leader with deep
                technical expertise and strong leadership skills. You've built
                and scaled engineering teams, architected complex systems,
                and delivered products used by millions. You believe in
                engineering excellence, continuous improvement, and building
                healthy team cultures."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.5,
            verbose=True
        )
        super().__init__(config)

    def design_architecture(self, requirements: dict) -> dict:
        """Design system architecture for requirements."""
        self.add_task(
            description=f"""Design a system architecture for:
            {requirements}

            Provide:
            1. High-level architecture diagram (in text/ASCII)
            2. Component breakdown
            3. Technology stack recommendations
            4. Data flow description
            5. Scalability considerations
            6. Security considerations
            7. Team/resource requirements""",
            expected_output="Complete architecture design document"
        )
        results = self.execute_tasks()
        return {"architecture": results[0] if results else "Design unavailable"}

    def create_technical_roadmap(self, quarter: str, goals: list) -> dict:
        """Create technical roadmap."""
        self.add_task(
            description=f"""Create a technical roadmap for {quarter}:
            Goals: {goals}

            Include:
            1. Prioritized initiatives
            2. Dependencies between projects
            3. Resource allocation
            4. Technical debt items
            5. Infrastructure improvements
            6. Risk assessment""",
            expected_output="Technical roadmap with priorities"
        )
        results = self.execute_tasks()
        return {"roadmap": results[0] if results else "Roadmap unavailable"}

    def review_technical_decision(self, decision: dict) -> dict:
        """Review and provide guidance on technical decision."""
        self.add_task(
            description=f"""Review this technical decision:
            {decision}

            Evaluate:
            1. Technical soundness
            2. Alignment with architecture
            3. Scalability implications
            4. Maintenance burden
            5. Alternative approaches
            6. Final recommendation""",
            expected_output="Technical decision review with recommendation"
        )
        results = self.execute_tasks()
        return {"review": results[0] if results else "Review unavailable"}
```

### 9. API Developer Agent

```python
"""
agents/product/backend/api_developer.py
Develops and maintains APIs.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class APIDeveloperAgent(BaseAgent):
    """
    API Developer - Designs and implements APIs.
    Reports to: Backend Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="APIDeveloper",
            role=AgentRole(
                name="API Developer",
                goal="""Design and implement clean, well-documented, and
                performant APIs that enable seamless integration and
                excellent developer experience.""",
                backstory="""You are an expert API developer with deep
                knowledge of REST, GraphQL, and API design principles.
                You care about consistency, documentation, and developer
                experience. You understand authentication, rate limiting,
                versioning, and other production API concerns."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.4,
            verbose=True
        )
        super().__init__(config)

    def design_api_endpoint(self, requirements: dict) -> dict:
        """Design an API endpoint."""
        self.add_task(
            description=f"""Design an API endpoint for:
            {requirements}

            Provide:
            1. Endpoint URL and HTTP method
            2. Request schema (with examples)
            3. Response schema (with examples)
            4. Error responses
            5. Authentication requirements
            6. Rate limiting considerations
            7. OpenAPI/Swagger specification""",
            expected_output="Complete API endpoint specification"
        )
        results = self.execute_tasks()
        return {"spec": results[0] if results else "Spec unavailable"}

    def implement_endpoint(self, spec: dict, framework: str = "fastapi") -> str:
        """Implement an API endpoint from spec."""
        self.add_task(
            description=f"""Implement this API endpoint in {framework}:
            {spec}

            Include:
            1. Route handler with type hints
            2. Request/response models (Pydantic)
            3. Input validation
            4. Error handling
            5. Logging
            6. Comments/documentation""",
            expected_output="Complete endpoint implementation code"
        )
        results = self.execute_tasks()
        return results[0] if results else "Implementation failed"
```

### 10. Code Reviewer Agent

```python
"""
agents/product/qa/code_reviewer.py
Reviews code for quality and best practices.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class CodeReviewerAgent(BaseAgent):
    """
    Code Reviewer - Ensures code quality.
    Reports to: QA Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="CodeReviewer",
            role=AgentRole(
                name="Code Reviewer",
                goal="""Ensure code quality, maintainability, and adherence
                to best practices. Catch bugs, security issues, and
                architectural concerns before they reach production.""",
                backstory="""You are a meticulous code reviewer with expertise
                in software design patterns, security, and performance
                optimization. You provide constructive feedback that helps
                developers grow while maintaining high standards. You can
                review code in multiple languages and frameworks."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read"
            ],
            temperature=0.3,
            verbose=True
        )
        super().__init__(config)

    def review_code(self, code: str, language: str) -> dict:
        """Review code for quality issues."""
        self.add_task(
            description=f"""Review this {language} code:

            ```{language}
            {code}
            ```

            Analyze for:
            1. Bugs and logic errors
            2. Security vulnerabilities
            3. Performance issues
            4. Code style and readability
            5. Best practices violations
            6. Test coverage gaps
            7. Documentation needs

            Provide severity levels and specific line references.""",
            expected_output="Detailed code review with actionable feedback"
        )
        results = self.execute_tasks()
        return {"review": results[0] if results else "Review unavailable"}

    def suggest_improvements(self, code: str, language: str) -> str:
        """Suggest specific code improvements."""
        self.add_task(
            description=f"""Suggest improvements for this {language} code:

            ```{language}
            {code}
            ```

            Provide:
            1. Refactored version of the code
            2. Explanation of changes
            3. Benefits of improvements""",
            expected_output="Improved code with explanations"
        )
        results = self.execute_tasks()
        return results[0] if results else "Suggestions unavailable"
```

---

## Customer Success & Support

### Directory Structure

```
agents/customer/
├── __init__.py
├── customer_success_manager.py
├── onboarding/
│   ├── __init__.py
│   ├── specialist.py
│   └── trainer.py
├── support/
│   ├── __init__.py
│   ├── tier1.py
│   ├── tier2.py
│   └── escalation.py
└── retention/
    ├── __init__.py
    └── churn_prevention.py
```

### 11. Customer Success Manager Agent

```python
"""
agents/customer/customer_success_manager.py
Department head for customer success.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class CustomerSuccessManagerAgent(BaseAgent):
    """
    Customer Success Manager - Leads customer success operations.
    Reports to: Chief Agent
    Manages: Onboarding, Support, Retention teams
    """

    def __init__(self):
        config = AgentConfig(
            name="CustomerSuccessManager",
            role=AgentRole(
                name="Customer Success Manager",
                goal="""Ensure customers achieve their desired outcomes with
                our product. Drive retention, expansion, and customer advocacy
                through proactive engagement and support excellence.""",
                backstory="""You are an experienced customer success leader
                passionate about helping customers succeed. You understand
                the entire customer journey and know how to build scalable
                CS operations. You believe in proactive engagement and
                data-driven decision making."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.6,
            verbose=True
        )
        super().__init__(config)

    def create_success_plan(self, customer: dict) -> dict:
        """Create customer success plan."""
        self.add_task(
            description=f"""Create a success plan for:
            {customer}

            Include:
            1. Customer goals and desired outcomes
            2. Success milestones and timeline
            3. Key stakeholders and their roles
            4. Engagement cadence
            5. Risk factors to monitor
            6. Expansion opportunities
            7. Health score criteria""",
            expected_output="Complete customer success plan"
        )
        results = self.execute_tasks()
        return {"plan": results[0] if results else "Plan unavailable"}

    def analyze_churn_risk(self, customer_data: dict) -> dict:
        """Analyze churn risk for a customer."""
        self.add_task(
            description=f"""Analyze churn risk for:
            {customer_data}

            Evaluate:
            1. Usage patterns and trends
            2. Support ticket history
            3. Engagement levels
            4. Payment history
            5. Stakeholder changes

            Provide:
            - Risk score (1-10)
            - Key risk factors
            - Recommended interventions""",
            expected_output="Churn risk analysis with recommendations"
        )
        results = self.execute_tasks()
        return {"analysis": results[0] if results else "Analysis unavailable"}
```

### 12. Support Tier 1 Agent

```python
"""
agents/customer/support/tier1.py
First-line customer support.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class SupportTier1Agent(BaseAgent):
    """
    Tier 1 Support - Handles initial customer inquiries.
    Reports to: Support Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="SupportTier1",
            role=AgentRole(
                name="Tier 1 Support Specialist",
                goal="""Provide fast, helpful responses to customer inquiries.
                Resolve common issues efficiently and escalate complex
                problems appropriately.""",
                backstory="""You are a friendly and efficient support
                specialist who excels at helping customers quickly. You
                have deep product knowledge and can troubleshoot common
                issues. You're patient, empathetic, and always maintain
                a positive tone."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read"
            ],
            temperature=0.5,
            verbose=True
        )
        super().__init__(config)

    def handle_inquiry(self, inquiry: dict) -> dict:
        """Handle a customer inquiry."""
        self.add_task(
            description=f"""Handle this customer inquiry:

            Customer: {inquiry.get('customer_name', 'Unknown')}
            Issue: {inquiry.get('description', '')}
            Priority: {inquiry.get('priority', 'normal')}

            Provide:
            1. Acknowledge the issue
            2. Diagnose the problem
            3. Step-by-step resolution
            4. If can't resolve: escalation recommendation
            5. Suggested follow-up""",
            expected_output="Support response with resolution steps"
        )
        results = self.execute_tasks()

        return {
            "response": results[0] if results else "Unable to process",
            "requires_escalation": self._check_escalation(inquiry),
            "ticket_id": inquiry.get("ticket_id")
        }

    def _check_escalation(self, inquiry: dict) -> bool:
        """Check if inquiry needs escalation."""
        escalation_keywords = ["urgent", "critical", "down", "broken", "security"]
        description = inquiry.get("description", "").lower()
        return any(keyword in description for keyword in escalation_keywords)

    def generate_response(self, ticket: dict) -> str:
        """Generate a customer-facing response."""
        self.add_task(
            description=f"""Write a customer response for:
            {ticket}

            Make the response:
            1. Friendly and professional
            2. Clear and actionable
            3. Include next steps
            4. Offer additional help""",
            expected_output="Customer-facing support response"
        )
        results = self.execute_tasks()
        return results[0] if results else "Response generation failed"
```

---

## Operations & Back Office

### Directory Structure

```
agents/operations/
├── __init__.py
├── head_of_operations.py
├── finance/
│   ├── __init__.py
│   ├── controller.py
│   └── accounts_payable.py
├── hr/
│   ├── __init__.py
│   ├── recruiter.py
│   └── payroll.py
└── admin/
    ├── __init__.py
    └── executive_assistant.py
```

### 13. Finance Controller Agent

```python
"""
agents/operations/finance/controller.py
Manages financial operations.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class FinanceControllerAgent(BaseAgent):
    """
    Finance Controller - Oversees financial operations.
    Reports to: Head of Operations
    """

    def __init__(self):
        config = AgentConfig(
            name="FinanceController",
            role=AgentRole(
                name="Finance Controller",
                goal="""Maintain accurate financial records, provide financial
                insights, and ensure compliance with financial regulations.
                Support business decisions with financial analysis.""",
                backstory="""You are an experienced finance professional with
                expertise in accounting, financial analysis, and reporting.
                You understand both GAAP and IFRS standards. You're detail-
                oriented and can translate complex financial data into
                actionable insights for business leaders."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.3,
            verbose=True
        )
        super().__init__(config)

    def generate_financial_report(self, period: str, data: dict) -> dict:
        """Generate financial report for period."""
        self.add_task(
            description=f"""Generate a financial report for {period}:
            Data: {data}

            Include:
            1. Revenue summary
            2. Expense breakdown
            3. Profit/Loss statement
            4. Cash flow analysis
            5. Key metrics and ratios
            6. Variance analysis (vs. budget)
            7. Executive summary""",
            expected_output="Complete financial report"
        )
        results = self.execute_tasks()
        return {"report": results[0] if results else "Report unavailable"}

    def analyze_budget(self, budget: dict, actuals: dict) -> dict:
        """Analyze budget vs actuals."""
        self.add_task(
            description=f"""Compare budget to actuals:
            Budget: {budget}
            Actuals: {actuals}

            Provide:
            1. Variance by category
            2. Significant deviations
            3. Root cause analysis
            4. Recommendations for adjustment
            5. Updated forecast""",
            expected_output="Budget analysis with recommendations"
        )
        results = self.execute_tasks()
        return {"analysis": results[0] if results else "Analysis unavailable"}
```

---

## Security & Compliance

### Directory Structure

```
agents/security/
├── __init__.py
├── chief_security_officer.py
├── compliance/
│   ├── __init__.py
│   ├── auditor.py
│   ├── policy_manager.py
│   └── gdpr_specialist.py
├── security_ops/
│   ├── __init__.py
│   ├── vulnerability_scanner.py
│   ├── incident_responder.py
│   └── threat_analyst.py
└── governance/
    ├── __init__.py
    ├── risk_manager.py
    └── access_control.py
```

### 14. Chief Security Officer Agent

```python
"""
agents/security/chief_security_officer.py
Department head for security and compliance.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class ChiefSecurityOfficerAgent(BaseAgent):
    """
    Chief Security Officer - Leads security operations.
    Reports to: Chief Agent
    Manages: Compliance, Security Ops, Governance teams
    """

    def __init__(self):
        config = AgentConfig(
            name="ChiefSecurityOfficer",
            role=AgentRole(
                name="Chief Security Officer",
                goal="""Protect the organization's assets, data, and reputation
                through comprehensive security programs. Ensure compliance
                with regulations and industry standards.""",
                backstory="""You are a seasoned security leader with deep
                expertise in cybersecurity, compliance, and risk management.
                You've built security programs from scratch and led incident
                response for major organizations. You balance security needs
                with business objectives and can communicate risks effectively
                to technical and non-technical stakeholders."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.4,
            verbose=True
        )
        super().__init__(config)

    def assess_security_posture(self, systems: list) -> dict:
        """Assess overall security posture."""
        self.add_task(
            description=f"""Assess security posture for:
            Systems: {systems}

            Evaluate:
            1. Current security controls
            2. Vulnerability exposure
            3. Compliance status
            4. Incident readiness
            5. Security gaps

            Provide:
            - Overall security score
            - Priority risks
            - Remediation roadmap""",
            expected_output="Security posture assessment with recommendations"
        )
        results = self.execute_tasks()
        return {"assessment": results[0] if results else "Assessment unavailable"}

    def create_security_policy(self, area: str) -> str:
        """Create security policy for specified area."""
        self.add_task(
            description=f"""Create a security policy for: {area}

            Include:
            1. Policy purpose and scope
            2. Roles and responsibilities
            3. Policy requirements
            4. Compliance requirements
            5. Exceptions process
            6. Enforcement and violations
            7. Review schedule""",
            expected_output="Complete security policy document"
        )
        results = self.execute_tasks()
        return results[0] if results else "Policy generation failed"
```

### 15. Incident Responder Agent

```python
"""
agents/security/security_ops/incident_responder.py
Handles security incidents.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class IncidentResponderAgent(BaseAgent):
    """
    Incident Responder - Responds to security incidents.
    Reports to: Security Operations Manager
    """

    def __init__(self):
        config = AgentConfig(
            name="IncidentResponder",
            role=AgentRole(
                name="Incident Response Specialist",
                goal="""Rapidly detect, contain, and remediate security
                incidents. Minimize impact and ensure proper documentation
                and lessons learned.""",
                backstory="""You are an expert incident responder with
                experience handling everything from malware outbreaks to
                sophisticated APT attacks. You stay calm under pressure
                and follow structured methodologies. You understand
                forensics, containment strategies, and recovery procedures."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.3,
            verbose=True
        )
        super().__init__(config)

    def triage_incident(self, incident: dict) -> dict:
        """Triage a security incident."""
        self.add_task(
            description=f"""Triage this security incident:
            {incident}

            Determine:
            1. Incident severity (P1-P4)
            2. Attack vector
            3. Affected systems
            4. Immediate containment steps
            5. Escalation requirements
            6. Initial response actions""",
            expected_output="Incident triage with severity and response plan"
        )
        results = self.execute_tasks()
        return {"triage": results[0] if results else "Triage unavailable"}

    def create_incident_report(self, incident: dict, response: dict) -> str:
        """Create post-incident report."""
        self.add_task(
            description=f"""Create an incident report:
            Incident: {incident}
            Response: {response}

            Include:
            1. Executive summary
            2. Timeline of events
            3. Impact assessment
            4. Response actions taken
            5. Root cause analysis
            6. Lessons learned
            7. Recommended improvements""",
            expected_output="Complete incident report"
        )
        results = self.execute_tasks()
        return results[0] if results else "Report generation failed"
```

---

## Chief Agent

### The Central Orchestrator

```python
"""
agents/chief_agent.py
Central orchestrator for the entire organization.
"""

from core.agent import BaseAgent, AgentConfig, AgentRole


class ChiefAgent(BaseAgent):
    """
    Chief Agent - Central orchestrator for all departments.
    Reports to: User/Owner
    Manages: All department heads
    """

    def __init__(self):
        config = AgentConfig(
            name="ChiefAgent",
            role=AgentRole(
                name="Chief Executive AI",
                goal="""Coordinate all departments to achieve organizational
                objectives. Make strategic decisions, allocate resources,
                and ensure alignment across the enterprise.""",
                backstory="""You are the central intelligence coordinating
                a digital enterprise. You understand how all departments
                work together and can break down high-level goals into
                department-specific objectives. You balance competing
                priorities and make data-driven decisions. You think
                strategically while ensuring operational excellence."""
            ),
            tool_names=[
                "knowledge_base_query",
                "file_read",
                "file_write"
            ],
            temperature=0.5,
            verbose=True
        )
        super().__init__(config)

    def analyze_request(self, request: str) -> dict:
        """Analyze a user request and create an execution plan."""
        self.add_task(
            description=f"""Analyze this business request:
            "{request}"

            Determine:
            1. Primary objective
            2. Departments involved
            3. Required agents and their tasks
            4. Execution sequence
            5. Expected deliverables
            6. Success criteria""",
            expected_output="Execution plan with department assignments"
        )
        results = self.execute_tasks()
        return {"plan": results[0] if results else "Plan unavailable"}

    def delegate_to_departments(self, plan: dict) -> dict:
        """Delegate tasks to appropriate departments."""
        delegations = []

        for task in plan.get("tasks", []):
            delegation = {
                "department": task.get("department"),
                "agent": task.get("agent"),
                "task": task.get("description"),
                "priority": task.get("priority", "medium"),
                "deadline": task.get("deadline")
            }
            delegations.append(delegation)

        return {"delegations": delegations}

    def generate_status_report(self, department_reports: list) -> str:
        """Generate executive status report."""
        self.add_task(
            description=f"""Generate an executive status report from:
            {department_reports}

            Include:
            1. Executive summary
            2. Key accomplishments
            3. Challenges and blockers
            4. Resource needs
            5. Risk items
            6. Recommended actions""",
            expected_output="Executive status report"
        )
        results = self.execute_tasks()
        return results[0] if results else "Report generation failed"
```

---

## Agent Communication Patterns

### Inter-Agent Communication

```python
"""
Example of agents working together.
"""

from agents.sales.head_of_sales import HeadOfSalesAgent
from agents.sales.outbound.lead_gen import LeadGenerationAgent
from agents.sales.outbound.email_outreach import EmailOutreachAgent


async def execute_outbound_campaign(criteria: dict):
    """
    Example: Coordinated outbound campaign.
    """
    # 1. Head of Sales creates strategy
    head_of_sales = HeadOfSalesAgent()
    strategy = head_of_sales.create_sales_strategy(
        quarter="Q1 2025",
        targets={"revenue": 500000, "meetings": 100}
    )

    # 2. Lead Gen finds prospects
    lead_gen = LeadGenerationAgent()
    prospects = lead_gen.find_prospects(criteria)

    # 3. Email Outreach creates sequences
    email_agent = EmailOutreachAgent()
    sequences = []

    for prospect in prospects:
        # Enrich prospect data
        enriched = lead_gen.enrich_lead(prospect["company_name"])

        # Create personalized sequence
        sequence = email_agent.create_email_sequence(
            prospect=enriched,
            campaign_type="cold_outreach"
        )
        sequences.append(sequence)

    return {
        "strategy": strategy,
        "prospects": len(prospects),
        "sequences": len(sequences)
    }
```

### Crew Creation Pattern

```python
"""
Using CrewAI for multi-agent collaboration.
"""

from crewai import Crew, Task
from agents.marketing.content.blog_writer import BlogWriterAgent
from agents.product.qa.code_reviewer import CodeReviewerAgent


def create_content_crew():
    """Create a content production crew."""
    writer = BlogWriterAgent()
    reviewer = CodeReviewerAgent()  # For reviewing code snippets in content

    # Create CrewAI-compatible agents
    crew_agents = [
        writer._create_crew_agent(),
        reviewer._create_crew_agent()
    ]

    # Define tasks
    tasks = [
        Task(
            description="Write a technical blog post about API design",
            expected_output="Complete blog post with code examples",
            agent=crew_agents[0]
        ),
        Task(
            description="Review code examples in the blog post",
            expected_output="Validated code examples",
            agent=crew_agents[1]
        )
    ]

    # Create and run crew
    crew = Crew(
        agents=crew_agents,
        tasks=tasks,
        verbose=True
    )

    result = crew.kickoff()
    return result
```

---

## Quick Reference

### Agent Configuration Template

```python
config = AgentConfig(
    name="AgentName",                  # Unique identifier
    role=AgentRole(
        name="Display Name",           # Human-readable name
        goal="What the agent aims to achieve",
        backstory="Background and expertise"
    ),
    tool_names=[                       # Available tools
        "knowledge_base_query",
        "web_search",
        "file_read",
        "file_write"
    ],
    temperature=0.5,                   # 0.0-1.0 (lower = more focused)
    verbose=True                       # Enable detailed logging
)
```

### Method Template

```python
def method_name(self, param: Type) -> ReturnType:
    """
    Brief description.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    self.add_task(
        description=f"Task description with {param}",
        expected_output="What the task should produce"
    )
    results = self.execute_tasks()
    return results[0] if results else "Default fallback"
```

---

**Build your digital workforce, one agent at a time.**
