from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel, Field
import os
from pathlib import Path

# Import CrewAI
from crewai import Agent, Task, Crew
# from crewai.agent import AgentType
CREWAI_AVAILABLE = True

# Import our components
from core.llm_singleton import get_singleton_llm
from knowledge_bases.kb_interface import get_kb_interface

# Try importing custom tools
try:
    from core.tools import get_tool_by_name
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    print("Warning: Custom tools are not available. Using placeholder tools.")

class AgentRole(BaseModel):
    """Role definition for an agent"""
    name: str = Field(..., description="Name of the role")
    description: str = Field(..., description="Description of the role")
    goal: str = Field(..., description="Goal of the agent in this role")
    backstory: str = Field(..., description="Backstory of the agent")

class AgentTools(BaseModel):
    """Tool configuration for an agent"""
    tool_names: List[str] = Field(default_factory=list, description="List of tool names to be used by the agent")

class AgentConfig(BaseModel):
    """Complete configuration for an agent"""
    id: str = Field(..., description="Unique identifier for the agent")
    role: AgentRole = Field(..., description="Role definition")
    tools: AgentTools = Field(default_factory=AgentTools, description="Tool configuration")
    tools_code: List[str] = Field(default_factory=list, description="List of tool codes to be loaded from tools.py")
    parent_id: Optional[str] = Field(None, description="ID of the parent agent")
    temperature: float = Field(0.7, description="Temperature for generation")
    verbose: bool = Field(False, description="Whether to log verbose output")
    department: str = Field("sales", description="Department the agent belongs to")
    python_class: Optional[str] = Field(None, description="Python class path for this agent")
    
class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, config: AgentConfig):
        """Initialize the agent with configuration"""
        self.config = config
        self.llm = get_singleton_llm()  # Use singleton LLM to prevent multiple model loading
        self.kb = get_kb_interface(config.department)
        self.tools = self._load_tools()
        self.crew_agent = self._create_crew_agent() if CREWAI_AVAILABLE else None
        self.tasks = []
        
    def _load_tools(self) -> List[Any]:
        """Load the specified tools for this agent"""
        tools = []
        
        # First, try to load tools from tools_code in config
        # This is the new approach from agents.yaml
        if hasattr(self.config, 'tools_code') and TOOLS_AVAILABLE:
            for tool_code in getattr(self.config, 'tools_code', []):
                tool = get_tool_by_name(tool_code)
                if tool:
                    tools.append(tool)
        
        # If no tools loaded yet or tools_code not defined, fall back to tool_names
        if not tools:
            for tool_name in self.config.tools.tool_names:
                if TOOLS_AVAILABLE:
                    # Try to match tool_name to a tool in tools.py
                    tool = get_tool_by_name(tool_name)
                    if tool:
                        tools.append(tool)
                        continue
                
                # Fall back to dummy tool if no real tool found
                tool = {
                    "name": tool_name,
                    "description": f"Tool for {tool_name}",
                    "func": lambda x: f"Result from {tool_name}: {x}"
                }
                tools.append(tool)
                
        return tools
    
    def _create_crew_agent(self) -> Any:
        """Create a CrewAI agent based on the configuration"""
        if not CREWAI_AVAILABLE:
            return None
            
        # In mock mode, don't create a CrewAI agent
        use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'
        if use_mock:
            # Return None to indicate we should use our own mock implementation
            return None
            
        # Try to create a CrewAI agent with our local LLM
        try:
            crew_agent = Agent(
                role=self.config.role.name,
                goal=self.config.role.goal,
                backstory=self.config.role.backstory,
                verbose=self.config.verbose,
                tools=self.tools if self.tools else [],
                llm=self.llm  # Pass our local LangChain LLM
            )
            print(f"✅ Created CrewAI agent with local LLM: {self.config.role.name}")
            return crew_agent
        except Exception as e:
            print(f"⚠️  CrewAI agent creation failed ({e}), using direct implementation")
            return None
    
    def add_task(self, description: str, expected_output: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add a task to the agent's queue"""
        # Check if we're in mock mode
        use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'
        
        if CREWAI_AVAILABLE and self.crew_agent and not use_mock:
            try:
                # In normal mode, try with context
                try:
                    task = Task(
                        description=description,
                        expected_output=expected_output,
                        agent=self.crew_agent,
                        context=context or {}
                    )
                except Exception as e:
                    print(f"Warning: Error creating task with context: {e}")
                    # Try as a fallback without context
                    task = Task(
                        description=description,
                        expected_output=expected_output,
                        agent=self.crew_agent
                    )
                
                self.tasks.append(task)
            except Exception as e:
                print(f"Error creating CrewAI task: {e}, falling back to mock task")
                # Fallback to mock task
                task = {
                    "description": description,
                    "expected_output": expected_output,
                    "context": context or {}
                }
                self.tasks.append(task)
        else:
            # Simple task structure for mock implementation
            task = {
                "description": description,
                "expected_output": expected_output,
                "context": context or {}
            }
            self.tasks.append(task)
    
    def execute_tasks(self) -> List[str]:
        """Execute all queued tasks and return the results"""
        results = []
        
        # If no tasks, return empty results
        if not self.tasks:
            return results
        
        # Check if we're in mock mode
        use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'
        
        if CREWAI_AVAILABLE and self.crew_agent and not use_mock:
            # Create a Crew with this agent and its tasks
            crew = Crew(
                agents=[self.crew_agent],
                tasks=self.tasks,
                verbose=self.config.verbose,
                memory=False  # Disable memory to avoid Chroma requirements
            )
            
            # Execute the tasks
            try:
                crew_results = crew.kickoff()
                if isinstance(crew_results, list):
                    results = crew_results
                else:
                    results = [crew_results]
            except Exception as e:
                print(f"Error executing tasks for agent {self.config.id}: {e}")
                # Fall back to mock implementation
                results = self._execute_tasks_mock()
        else:
            # Mock implementation for when CrewAI is not available or in mock mode
            results = self._execute_tasks_mock()
        
        # Clear the task queue
        self.tasks = []
        
        return results
        
    def _execute_tasks_mock(self) -> List[str]:
        """Execute tasks using the mock implementation"""
        results = []
        
        for task in self.tasks:
            try:
                if isinstance(task, dict):
                    # Handle mock task
                    description = task.get("description", "")
                    expected_output = task.get("expected_output", "")
                    context = task.get("context", {})
                else:
                    # Handle CrewAI Task object
                    description = task.description
                    expected_output = task.expected_output
                    context = task.context
                
                # Check if we're in mock mode
                use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'
                
                if use_mock:
                    # In mock mode, generate a plausible demo response based on the task
                    if "lead" in description.lower() and "generat" in description.lower():
                        # Generate mock lead data
                        mock_response = self._generate_mock_lead_data(description)
                    elif "research" in description.lower():
                        # Generate mock research data
                        mock_response = self._generate_mock_research_data(description)
                    else:
                        # Generic mock response
                        mock_response = f"Mock response for task: {description[:50]}..."
                    
                    results.append(mock_response)
                else:
                    # Use the LLM in non-mock mode
                    system_prompt = f"""You are {self.config.role.name}, a {self.config.role.description}.
                    Your goal is: {self.config.role.goal}
                    Backstory: {self.config.role.backstory}
                    
                    Always respond in a professional manner, focusing on your expertise area.
                    """
                    
                    user_prompt = f"""Task: {description}
                    
                    Expected output: {expected_output}
                    
                    Context: {context}
                    
                    Please complete this task to the best of your ability.
                    """
                    
                    # Use the LLM to generate a response
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    response = self.llm(full_prompt)
                    results.append(response)
            except Exception as e:
                print(f"Error executing task: {e}")
                results.append(f"Error: {e}")
        
        return results
    
    def _generate_mock_lead_data(self, description: str) -> str:
        """Generate mock lead data for demo purposes"""
        return """Lead 1:
Name: Sarah Johnson
Title: Director of Operations
Company: Elevate Coaching Solutions
Email: sarah.johnson@elevatecoaching.com
Phone: (415) 555-7890
Website: www.elevatecoaching.com
Employees: 12
Industry: Professional Development & Executive Coaching
Location: San Francisco, CA
LinkedIn: linkedin.com/in/sarahjohnson-elevate
Notes: Perfect match for our ICP - small coaching business with dedicated operations lead looking to scale. Currently using multiple disconnected systems for client management.

Lead 2:
Name: Michael Chen
Title: CEO & Founder
Company: Growth Catalyst Coaching
Email: michael@growthcatalyst.co
Phone: (312) 555-4321
Website: www.growthcatalyst.co
Employees: 8
Industry: Business Coaching & Consulting
Location: Chicago, IL
LinkedIn: linkedin.com/in/michaelchen-growth
Notes: Rapidly growing coaching practice with 15+ contractors in addition to employees. Tech-savvy founder looking for streamlined systems to manage client relationships.

Lead 3:
Name: Rebecca Williams
Title: Operations Manager
Company: Momentum Leadership Group
Email: rwilliams@momentumleadership.com
Phone: (214) 555-9876
Website: www.momentumleadership.com
Employees: 23
Industry: Leadership Development & Team Coaching
Location: Austin, TX
LinkedIn: linkedin.com/in/rebeccawilliams-momentum
Notes: Mid-sized coaching firm experiencing growing pains with client management. Currently using a mix of Asana, Google Drive, and Calendly - looking for an integrated solution."""
        
    def _generate_mock_research_data(self, description: str) -> str:
        """Generate mock research data for demo purposes"""
        return """# Company Research Report: Elevate Coaching Solutions

## Company Overview
Elevate Coaching Solutions is a boutique coaching firm founded in 2018 by former tech executive Jennifer Parsons. The company has grown steadily to 12 full-time employees with an additional network of 8-10 contract coaches. They specialize in executive coaching, leadership development, and team performance programs for technology and healthcare organizations.

## Industry and Market Position
They operate in the professional development and executive coaching space, which has seen significant growth over the past 5 years. Elevate positions itself as a premium, tech-enabled coaching solution that bridges traditional executive coaching with data-driven approaches. They compete primarily with larger coaching networks like BetterUp and CoachHub, but differentiate through their industry specialization and high-touch approach.

## Recent News and Developments
The company recently secured a partnership with Salesforce to provide coaching services to their mid-level managers. They were also featured in Forbes' "Top 50 Coaching Firms to Watch" last quarter. Their latest press release indicates they're planning to expand their services to include specialized coaching for technical leaders and CTOs.

## Current Technologies
Based on their job postings and LinkedIn profiles, they appear to be using:
- Salesforce for CRM
- Asana for project management
- Calendly for scheduling
- Google Workspace for file sharing and collaboration
- Zoom for virtual coaching sessions
- Various disconnected tools for tracking client progress and engagement

## Pain Points Related to Client Management
- Scattered client information across multiple platforms
- Difficulty tracking coach-client interactions and progress
- Manual processes for matching clients with appropriate coaches
- Limited visibility into overall client satisfaction and program effectiveness
- Time-consuming reporting and analytics processes

## Decision-Making Structure
Sarah Johnson (Director of Operations) appears to be the key decision-maker for operational tools and systems. The CEO, Jennifer Parsons, would likely be involved in final approval for significant investments. They also have a Technical Operations Specialist (Alex Rivera) who would likely influence technology decisions.

## Potential Entry Points
1. Their growing coach network requires better systems for managing coach-client relationships
2. The Salesforce partnership creates an immediate need for more streamlined client management
3. Their current tech stack appears fragmented, creating an opportunity for a unified solution
4. Their focus on data-driven coaching aligns well with our analytics capabilities

Recommendation: Approach Sarah Johnson with a demo focused on coach management, client progress tracking, and Salesforce integration capabilities."""

    
    def direct_query(self, query: str, system_prompt: Optional[str] = None) -> str:
        """Direct query to the agent's LLM"""
        if system_prompt is None:
            system_prompt = f"""You are {self.config.role.name}. {self.config.role.description}
            Your goal is: {self.config.role.goal}
            Backstory: {self.config.role.backstory}
            
            Always respond in a professional manner, focusing on your expertise area.
            """
        
        full_prompt = f"{system_prompt}\n\n{query}"
        return self.llm(full_prompt)

    def delegate_to_child(self, child_id: str, task_description: str, expected_output: str) -> Optional[str]:
        """Delegate a task to a child agent if available"""
        # This would be implemented by the specific agent class
        raise NotImplementedError("Delegation must be implemented by specific agent classes")
