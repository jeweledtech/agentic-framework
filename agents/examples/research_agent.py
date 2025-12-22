"""
Research Agent Example

This example demonstrates how to create a research agent that can search
for information and compile research reports.
"""

from typing import List, Dict, Any, Optional
from core.agent import BaseAgent, AgentConfig


class ResearchAgent(BaseAgent):
    """
    A research agent that can search for information and compile reports.
    
    This agent demonstrates:
    - How to extend the BaseAgent class
    - How to use tools for web search and knowledge base queries
    - How to structure agent responses
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the research agent with configuration"""
        if config is None:
            # Create a default configuration if none provided
            from core.agent import AgentRole, AgentTools
            config = AgentConfig(
                id="research_agent",
                role=AgentRole(
                    name="Research Specialist",
                    description="An agent specialized in researching topics and compiling comprehensive reports",
                    goal="Find accurate, relevant information and present it in a clear, structured format",
                    backstory="You are an experienced researcher with expertise in finding and synthesizing information from multiple sources."
                ),
                tools=AgentTools(
                    tool_names=["web_search", "knowledge_base_query"]
                ),
                department="research",
                temperature=0.3  # Lower temperature for more focused research
            )
        
        super().__init__(config)
    
    def research_topic(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """
        Research a topic and return structured findings
        
        Args:
            topic: The topic to research
            depth: Level of detail ("basic", "medium", "comprehensive")
            
        Returns:
            Dictionary containing research findings
        """
        # Define the research task
        task_description = f"""
        Research the topic: {topic}
        
        Please provide a {depth} level analysis including:
        1. Overview and definition
        2. Key concepts and terminology
        3. Current trends and developments
        4. Practical applications
        5. Future outlook
        
        Use available tools to gather information and cite sources where possible.
        """
        
        expected_output = f"""
        A structured research report on {topic} with:
        - Executive summary
        - Detailed findings organized by section
        - Key takeaways
        - References and sources
        """
        
        # Add the task and execute
        self.add_task(task_description, expected_output)
        results = self.execute_tasks()
        
        # Structure the response
        return {
            "topic": topic,
            "depth": depth,
            "findings": results[0] if results else "No findings available",
            "status": "completed"
        }
    
    def compare_topics(self, topics: List[str]) -> Dict[str, Any]:
        """
        Compare multiple topics and highlight similarities and differences
        
        Args:
            topics: List of topics to compare
            
        Returns:
            Comparison analysis
        """
        topics_str = ", ".join(topics)
        
        task_description = f"""
        Compare and contrast the following topics: {topics_str}
        
        Provide:
        1. Brief overview of each topic
        2. Key similarities
        3. Major differences
        4. Use cases for each
        5. Recommendations on when to use each
        """
        
        expected_output = "A comprehensive comparison table and analysis"
        
        self.add_task(task_description, expected_output)
        results = self.execute_tasks()
        
        return {
            "topics": topics,
            "comparison": results[0] if results else "No comparison available",
            "status": "completed"
        }
    
    def fact_check(self, statement: str) -> Dict[str, Any]:
        """
        Fact-check a statement and provide verification
        
        Args:
            statement: The statement to fact-check
            
        Returns:
            Fact-checking results with sources
        """
        task_description = f"""
        Fact-check the following statement: "{statement}"
        
        Provide:
        1. Verification status (True/False/Partially True/Unverifiable)
        2. Supporting evidence
        3. Contradicting evidence (if any)
        4. Reliable sources
        5. Context and nuance
        """
        
        expected_output = "Detailed fact-checking report with sources"
        
        self.add_task(task_description, expected_output)
        results = self.execute_tasks()
        
        return {
            "statement": statement,
            "verification": results[0] if results else "Unable to verify",
            "status": "completed"
        }