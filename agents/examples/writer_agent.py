"""
Writer Agent Example

This example demonstrates how to create a writer agent that can generate
various types of content based on research and guidelines.
"""

from typing import Dict, Any, Optional, List
from core.agent import BaseAgent, AgentConfig


class WriterAgent(BaseAgent):
    """
    A writer agent that can create various types of content.
    
    This agent demonstrates:
    - Content generation capabilities
    - Collaboration with other agents (like ResearchAgent)
    - Different writing styles and formats
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the writer agent with configuration"""
        if config is None:
            # Create a default configuration if none provided
            from core.agent import AgentRole, AgentTools
            config = AgentConfig(
                id="writer_agent",
                role=AgentRole(
                    name="Content Writer",
                    description="An agent specialized in creating engaging, well-structured content",
                    goal="Write clear, compelling content that effectively communicates ideas to the target audience",
                    backstory="You are a skilled writer with experience in various content formats, from technical documentation to creative storytelling."
                ),
                tools=AgentTools(
                    tool_names=["knowledge_base_query", "file_write"]
                ),
                department="content",
                temperature=0.7  # Balanced temperature for creative yet coherent writing
            )
        
        super().__init__(config)
    
    def write_blog_post(self, topic: str, research_data: Optional[str] = None, 
                       tone: str = "professional", word_count: int = 800) -> Dict[str, Any]:
        """
        Write a blog post on a given topic
        
        Args:
            topic: The topic for the blog post
            research_data: Optional research data to base the post on
            tone: Writing tone (professional, casual, technical, creative)
            word_count: Target word count
            
        Returns:
            Dictionary containing the blog post and metadata
        """
        context = f"Research data: {research_data}" if research_data else ""
        
        task_description = f"""
        Write a {tone} blog post about: {topic}
        Target word count: {word_count} words
        
        {context}
        
        Structure:
        1. Engaging headline
        2. Compelling introduction
        3. Well-organized body sections with subheadings
        4. Practical examples or case studies
        5. Strong conclusion with call-to-action
        
        Optimize for readability and SEO.
        """
        
        expected_output = f"A complete {word_count}-word blog post with title, sections, and meta description"
        
        self.add_task(task_description, expected_output)
        results = self.execute_tasks()
        
        return {
            "topic": topic,
            "tone": tone,
            "content": results[0] if results else "No content generated",
            "word_count": word_count,
            "status": "completed"
        }
    
    def create_technical_documentation(self, subject: str, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create technical documentation for a subject
        
        Args:
            subject: The subject to document
            specifications: Technical specifications and requirements
            
        Returns:
            Technical documentation
        """
        specs_str = "\n".join([f"- {k}: {v}" for k, v in specifications.items()])
        
        task_description = f"""
        Create comprehensive technical documentation for: {subject}
        
        Specifications:
        {specs_str}
        
        Include:
        1. Overview and purpose
        2. Prerequisites and requirements
        3. Step-by-step instructions
        4. Code examples (if applicable)
        5. Troubleshooting guide
        6. API reference (if applicable)
        7. Best practices
        """
        
        expected_output = "Complete technical documentation in markdown format"
        
        self.add_task(task_description, expected_output)
        results = self.execute_tasks()
        
        return {
            "subject": subject,
            "documentation": results[0] if results else "No documentation generated",
            "format": "markdown",
            "status": "completed"
        }
    
    def write_email(self, recipient: str, subject: str, purpose: str, 
                   tone: str = "professional", key_points: List[str] = None) -> Dict[str, Any]:
        """
        Write a professional email
        
        Args:
            recipient: The recipient's role/name
            subject: Email subject line
            purpose: The purpose of the email
            tone: Email tone (professional, friendly, formal, casual)
            key_points: List of key points to include
            
        Returns:
            Email content
        """
        points_str = "\n".join([f"- {point}" for point in (key_points or [])])
        
        task_description = f"""
        Write a {tone} email to {recipient}
        Subject: {subject}
        Purpose: {purpose}
        
        Key points to include:
        {points_str}
        
        Ensure the email is:
        - Clear and concise
        - Appropriately formatted
        - Action-oriented (if applicable)
        - Professional yet personable
        """
        
        expected_output = "Complete email with subject line and body"
        
        self.add_task(task_description, expected_output)
        results = self.execute_tasks()
        
        return {
            "recipient": recipient,
            "subject": subject,
            "email_content": results[0] if results else "No email generated",
            "tone": tone,
            "status": "completed"
        }
    
    def summarize_content(self, content: str, max_words: int = 150) -> Dict[str, Any]:
        """
        Summarize long content into a concise version
        
        Args:
            content: The content to summarize
            max_words: Maximum words for the summary
            
        Returns:
            Summary of the content
        """
        task_description = f"""
        Summarize the following content in {max_words} words or less:
        
        {content}
        
        The summary should:
        - Capture all key points
        - Maintain the original meaning
        - Be clear and concise
        - Use bullet points if helpful
        """
        
        expected_output = f"A clear, concise summary under {max_words} words"
        
        self.add_task(task_description, expected_output)
        results = self.execute_tasks()
        
        return {
            "summary": results[0] if results else "No summary generated",
            "word_limit": max_words,
            "status": "completed"
        }