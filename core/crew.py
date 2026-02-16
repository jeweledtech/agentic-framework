"""
Crew orchestration module for the agentic system.

This module provides classes and functions for loading agent configurations
from YAML files, creating crews of agents, and running tasks.

Execution modes:
- CrewAI mode: If crewai is installed, uses Crew.kickoff() for orchestration
- Direct mode: Executes crew tasks sequentially via each agent's direct LLM path
- Mock mode: Returns demo data when USE_MOCK_KB=true
"""

import os
import yaml
from typing import Dict, List, Any, Optional, Type, Union
from pathlib import Path
import importlib
import inspect

# Import CrewAI (optional — framework works without it)
try:
    from crewai import Agent, Task, Crew
    import crewai.process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    Agent = None
    Task = None
    Crew = None
    print("Info: CrewAI not installed. Crews will use direct LLM execution.")

# Import our components
from core.agent import BaseAgent, AgentConfig, AgentRole, AgentTools
from core.llm_singleton import get_singleton_llm
from knowledge_bases.kb_interface import get_kb_interface

# Get the project root directory
PROJECT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = PROJECT_DIR / 'config'
AGENTS_CONFIG_PATH = CONFIG_DIR / 'agents.yaml'
TASKS_CONFIG_PATH = CONFIG_DIR / 'tasks.yaml'

class AgentLoader:
    """Utility class for loading agent configurations and creating agent instances"""

    @staticmethod
    def load_agent_configs() -> Dict[str, AgentConfig]:
        """Load agent configurations from YAML file"""
        if not AGENTS_CONFIG_PATH.exists():
            raise FileNotFoundError(f"Agent configuration file not found at {AGENTS_CONFIG_PATH}")

        with open(AGENTS_CONFIG_PATH, 'r') as f:
            config_data = yaml.safe_load(f)

        agent_configs = {}
        for agent_id, agent_data in config_data.items():
            # Create the agent configuration object
            agent_config = AgentConfig(
                id=agent_data.get('id', agent_id),
                role=AgentRole(
                    name=agent_data['role']['name'],
                    description=agent_data['role']['description'],
                    goal=agent_data['role']['goal'],
                    backstory=agent_data['role']['backstory']
                ),
                tools=AgentTools(
                    tool_names=agent_data.get('tools', {}).get('tool_names', [])
                ),
                parent_id=agent_data.get('parent_id'),
                temperature=agent_data.get('temperature', 0.7),
                verbose=agent_data.get('verbose', False),
                department=agent_data.get('department', 'sales')
            )

            agent_configs[agent_id] = agent_config

        return agent_configs

    @staticmethod
    def find_agent_class(agent_id: str) -> Type[BaseAgent]:
        """Find the agent class for a given agent ID"""
        # Define the mapping of agent IDs to class paths
        agent_class_paths = {
            # Chief Agent
            'chief_agent': 'agents.chief_agent.ChiefAgent',

            # Sales Department
            'head_of_sales': 'agents.sales.head_of_sales.HeadOfSalesAgent',
            'outbound_sales_manager': 'agents.sales.outbound.manager.OutboundSalesManager',
            'inbound_sales_manager': 'agents.sales.inbound.manager.InboundSalesManager',

            # Outbound Sales Team
            'lead_generation_agent': 'agents.sales.outbound.lead_gen.LeadGenerationAgent',
            'email_outreach_agent': 'agents.sales.outbound.email.EmailOutreachAgent',
            'crm_update_agent': 'agents.sales.outbound.crm.CRMUpdateAgent',

            # Inbound Sales Team
            'sequence_agent': 'agents.sales.inbound.sequence.SequenceAgent',
            'lead_prioritization_agent': 'agents.sales.inbound.prioritize.LeadPrioritizationAgent',
            'inbound_crm_agent': 'agents.sales.inbound.crm.InboundCRMAgent',

            # Marketing Department
            'head_of_content': 'agents.marketing.head_of_content.HeadOfContentAgent',
            'video_content_manager': 'agents.marketing.video_content_manager.VideoContentManagerAgent',
            'content_ideation_agent': 'agents.marketing.content_ideation_agent.ContentIdeationAgent',

            # Product Department
            'head_of_engineering': 'agents.product.head_of_engineering.HeadOfEngineeringAgent',
            'front_end_copilot_manager': 'agents.product.front_end_copilot_manager.FrontEndCoPilotManagerAgent',
            'back_end_copilot_manager': 'agents.product.back_end_copilot_manager.BackEndCoPilotManagerAgent',
            'testing_manager': 'agents.product.testing_manager.TestingManagerAgent',

            # Back Office Department
            'finance_guru': 'agents.back_office.finance_guru.FinanceGuruAgent',
            'payroll_manager': 'agents.back_office.payroll_manager.PayrollManagerAgent',
            'grant_specialist': 'agents.back_office.grant_specialist.GrantSpecialistAgent',

            # Customer Department
            'customer_success_manager': 'agents.customer.customer_success_manager.CustomerSuccessManagerAgent',
            'support_lead': 'agents.customer.support_lead.SupportLeadAgent',
            'onboarding_specialist': 'agents.customer.onboarding_specialist.OnboardingSpecialistAgent',

            # Admin Department
            'head_of_admin': 'agents.admin.head_of_admin.HeadOfAdminAgent',
            'executive_asst_manager': 'agents.admin.executive_asst_manager.ExecutiveAsstManagerAgent',
            'scheduling_agent_admin': 'agents.admin.executive_support.scheduling.SchedulingAgent',
        }

        if agent_id not in agent_class_paths:
            raise ValueError(f"No agent class mapping defined for agent ID: {agent_id}")

        class_path = agent_class_paths[agent_id]
        module_path, class_name = class_path.rsplit('.', 1)

        try:
            # Try to import the module
            module = importlib.import_module(module_path)

            # Get the class from the module
            agent_class = getattr(module, class_name)

            # Verify that it's a subclass of BaseAgent
            if not issubclass(agent_class, BaseAgent):
                raise TypeError(f"Class {class_name} is not a subclass of BaseAgent")

            return agent_class
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not import agent class for {agent_id}: {e}")

            # Return the BaseAgent as a fallback
            return BaseAgent

    @staticmethod
    def create_agent(agent_id: str) -> BaseAgent:
        """Create an agent instance for a given agent ID"""
        # Load all agent configurations
        agent_configs = AgentLoader.load_agent_configs()

        if agent_id not in agent_configs:
            raise ValueError(f"No configuration found for agent ID: {agent_id}")

        # Get the agent configuration
        agent_config = agent_configs[agent_id]

        # Find the agent class
        agent_class = AgentLoader.find_agent_class(agent_id)

        # Create and return the agent instance
        try:
            # Check if the agent class constructor expects specific parameters
            signature = inspect.signature(agent_class.__init__)

            if len(signature.parameters) == 1:  # Just 'self'
                # Class doesn't explicitly define __init__ or has no params
                agent = agent_class()
            else:
                # Create the agent with the configuration
                agent = agent_class(agent_config)

            return agent
        except Exception as e:
            print(f"Error creating agent {agent_id}: {e}")
            # Fallback to base agent if there's an error
            return BaseAgent(agent_config)


class TaskLoader:
    """Utility class for loading task configurations"""

    @staticmethod
    def load_task_configs() -> Dict[str, Dict[str, Any]]:
        """Load task configurations from YAML file"""
        if not TASKS_CONFIG_PATH.exists():
            raise FileNotFoundError(f"Task configuration file not found at {TASKS_CONFIG_PATH}")

        with open(TASKS_CONFIG_PATH, 'r') as f:
            config_data = yaml.safe_load(f)

        return config_data

    @staticmethod
    def get_task_config(task_id: str) -> Dict[str, Any]:
        """Get a specific task configuration"""
        task_configs = TaskLoader.load_task_configs()

        if task_id not in task_configs:
            raise ValueError(f"No configuration found for task ID: {task_id}")

        return task_configs[task_id]

    @staticmethod
    def create_task(task_id: str, agent: Union[BaseAgent, str], context: Dict[str, Any] = None) -> Any:
        """Create a task for a given task ID and agent.

        Returns a CrewAI Task if available, otherwise a dict-based task.
        """
        # Get the task configuration
        task_config = TaskLoader.get_task_config(task_id)

        # If the agent is a string (agent ID), create the agent
        if isinstance(agent, str):
            agent = AgentLoader.create_agent(agent)

        # Format the description and expected output with context values
        description = task_config['description']
        expected_output = task_config['expected_output']

        if context:
            for key, value in context.items():
                placeholder = "{" + key + "}"
                if placeholder in description:
                    description = description.replace(placeholder, str(value))
                if placeholder in expected_output:
                    expected_output = expected_output.replace(placeholder, str(value))

        # Create CrewAI task if available and agent has a crew_agent
        if CREWAI_AVAILABLE and hasattr(agent, 'crew_agent') and agent.crew_agent:
            try:
                task = Task(
                    description=description,
                    expected_output=expected_output,
                    agent=agent.crew_agent
                )
                return task
            except Exception as e:
                print(f"Warning: CrewAI task creation failed ({e}), using dict task")

        # Dict-based task (works with direct LLM execution)
        return {
            "id": task_id,
            "description": description,
            "expected_output": expected_output,
            "agent": agent,
            "context": context or {}
        }


class CrewBuilder:
    """Utility class for building and running crews of agents.

    Supports two execution modes:
    - CrewAI: Uses Crew.kickoff() when crewai is installed
    - Direct: Executes tasks sequentially via each agent's LLM
    """

    @staticmethod
    def create_crew(name: str, agents: List[Union[BaseAgent, str]], tasks: List[Any] = None) -> Any:
        """Create a crew of agents.

        Returns a CrewAI Crew object if available, otherwise a dict-based crew
        that can be executed via run_crew().
        """
        # Resolve agent IDs to instances
        original_agents = []
        for agent in agents:
            if isinstance(agent, str):
                original_agents.append(AgentLoader.create_agent(agent))
            else:
                original_agents.append(agent)

        use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'

        # Try CrewAI path
        if CREWAI_AVAILABLE and not use_mock:
            crew_agents = []
            for agent in original_agents:
                if hasattr(agent, 'crew_agent') and agent.crew_agent:
                    crew_agents.append(agent.crew_agent)

            if crew_agents:
                # Extract/convert tasks to CrewAI Task objects
                crew_tasks = []
                if tasks:
                    for task in tasks:
                        if isinstance(task, dict) and 'description' in task and 'expected_output' in task:
                            agent_for_task = task.get('agent')
                            if hasattr(agent_for_task, 'crew_agent') and agent_for_task.crew_agent:
                                try:
                                    crew_task = Task(
                                        description=task['description'],
                                        expected_output=task['expected_output'],
                                        agent=agent_for_task.crew_agent
                                    )
                                    crew_tasks.append(crew_task)
                                except Exception:
                                    crew_tasks.append(task)
                            else:
                                crew_tasks.append(task)
                        else:
                            crew_tasks.append(task)

                try:
                    return Crew(
                        agents=crew_agents,
                        tasks=crew_tasks,
                        verbose=True,
                        process=crewai.process.Process.sequential,
                        memory=False
                    )
                except Exception as e:
                    print(f"Warning: CrewAI Crew creation failed ({e}), using direct execution")

        # Dict-based crew for direct execution
        return {
            "name": name,
            "agents": original_agents,
            "tasks": tasks or [],
            "verbose": True
        }

    @staticmethod
    def run_crew(crew: Any) -> Any:
        """Run a crew and return the results.

        If crew is a CrewAI Crew, calls kickoff().
        If crew is a dict, executes tasks sequentially via direct LLM.
        """
        use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'

        # Dict-based crew → direct execution
        if isinstance(crew, dict):
            return CrewBuilder._run_crew_direct(crew)

        # CrewAI Crew object
        if not use_mock:
            try:
                results = crew.kickoff()
                return results
            except Exception as e:
                print(f"Error running CrewAI crew: {e}")
                import traceback
                traceback.print_exc()
                # Fall through to direct execution if possible
                return [f"Error: {e}"]

        # Fallback
        return CrewBuilder._run_crew_direct(crew)

    @staticmethod
    def _run_crew_direct(crew: Any) -> List[str]:
        """Execute crew tasks sequentially via each agent's direct LLM path.

        This is the default execution mode when CrewAI is not installed.
        Each task is routed to its assigned agent, which calls the LLM directly.
        """
        name = crew.get('name', 'unnamed') if isinstance(crew, dict) else str(crew)
        print(f"Executing crew '{name}' via direct LLM...")

        results = []

        if isinstance(crew, dict) and 'tasks' in crew:
            for task in crew['tasks']:
                task_desc = task.get('description', 'Unknown task')[:60] if isinstance(task, dict) else str(task)[:60]
                print(f"  Running task: {task_desc}...")

                if isinstance(task, dict) and isinstance(task.get('agent'), BaseAgent):
                    agent = task['agent']
                    agent.add_task(
                        task['description'],
                        task['expected_output'],
                        task.get('context')
                    )
                    task_results = agent.execute_tasks()
                    results.extend(task_results)
                elif isinstance(task, dict):
                    results.append(f"Result for task: {task.get('description', 'Unknown task')}")
                else:
                    results.append(f"Result for task: {str(task)[:100]}")
        else:
            # No tasks — generate placeholder results from agents
            agents = crew.get('agents', []) if isinstance(crew, dict) else []
            for agent in agents:
                if hasattr(agent, 'config'):
                    results.append(f"Agent {agent.config.id} ready (no tasks assigned)")

        return results


class OrganizationBuilder:
    """Utility class for building organizational structures of agents"""

    @staticmethod
    def build_department(department_id: str) -> Dict[str, BaseAgent]:
        """Build all agents for a department"""
        agent_configs = AgentLoader.load_agent_configs()

        # Find all agents belonging to the department
        department_agent_ids = [
            agent_id for agent_id, config in agent_configs.items()
            if config.department == department_id
        ]

        # Create all the agents
        department_agents = {}
        for agent_id in department_agent_ids:
            try:
                agent = AgentLoader.create_agent(agent_id)
                department_agents[agent_id] = agent
            except Exception as e:
                print(f"Error creating agent {agent_id}: {e}")

        return department_agents

    @staticmethod
    def build_organization() -> Dict[str, Dict[str, BaseAgent]]:
        """Build the entire organization of agents"""
        agent_configs = AgentLoader.load_agent_configs()

        # Get all departments
        departments = set(config.department for config in agent_configs.values())

        # Build each department
        organization = {}
        for department in departments:
            organization[department] = OrganizationBuilder.build_department(department)

        return organization


# Example usage
if __name__ == "__main__":
    # Test loading agent configurations
    print("Loading agent configurations...")
    agent_configs = AgentLoader.load_agent_configs()
    print(f"Loaded {len(agent_configs)} agent configurations")

    # Test creating an agent
    print("\nCreating lead generation agent...")
    lead_gen_agent = AgentLoader.create_agent("lead_generation_agent")
    print(f"Created agent: {lead_gen_agent.config.role.name}")

    # Test loading task configurations
    print("\nLoading task configurations...")
    task_configs = TaskLoader.load_task_configs()
    print(f"Loaded {len(task_configs)} task configurations")

    # Test creating a task
    print("\nCreating a generate leads task...")
    generate_leads_task = TaskLoader.create_task("generate_leads", lead_gen_agent, {
        "quantity": 3,
        "criteria": "Coaching businesses with 5-50 employees"
    })

    # Test building a crew
    print(f"\nCrewAI available: {CREWAI_AVAILABLE}")
    print("Creating a crew...")
    crew = CrewBuilder.create_crew("Outbound Sales Crew", [lead_gen_agent], [generate_leads_task])

    print("\nRunning the crew...")
    results = CrewBuilder.run_crew(crew)
    print(f"Results: {results}")
