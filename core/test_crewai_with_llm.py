#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Display the current Python path for debugging
print("Current sys.path:")
for p in sys.path:
    print(f"  - {p}")

# Add the virtual environment site-packages to the path if needed
venv_site_packages = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'lib', 'python3.11', 'site-packages')
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    print(f"Adding virtual environment path: {venv_site_packages}")
    sys.path.insert(0, venv_site_packages)

# Add current directory to path if needed
if '.' not in sys.path:
    print("Adding current directory to path")
    sys.path.append('.')

def test_crewai_with_real_llm():
    """Test if CrewAI is available and working with our LLM"""
    try:
        # Try importing CrewAI
        import crewai
        print(f"✅ CrewAI is installed (version: {crewai.__version__})")
        print(f"Location: {crewai.__file__}")
        
        # Import needed CrewAI components
        from crewai import Agent, Task, Crew
        
        # Try to import our LangChain compatible LLM
        from core.llm_for_crewai import get_langchain_llm
        llm = get_langchain_llm()
        print("✅ Successfully created LangChain compatible LLM")
        
        # Create a simple agent with our LLM
        agent = Agent(
            role="Test Agent",
            goal="To test CrewAI integration with our LLM",
            backstory="A simple agent for testing with our LLM",
            verbose=True,
            llm=llm
        )
        print(f"✅ Successfully created a CrewAI Agent with our LLM")
        
        # Create a simple task
        task = Task(
            description="Say hello and introduce yourself in one sentence", 
            expected_output="A brief, friendly introduction",
            agent=agent
        )
        print(f"✅ Successfully created a CrewAI Task")
        
        # Create a simple crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        print(f"✅ Successfully created a CrewAI Crew")
        
        print("✅ CrewAI initialization test passed")
        
        # Try executing the task
        print("\nExecuting task with CrewAI and our LLM...")
        result = crew.kickoff()
        print(f"✅ Successfully executed task")
        print(f"\nResult: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing CrewAI with our LLM: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing CrewAI Integration with Our LLM ===")
    success = test_crewai_with_real_llm()
    
    if success:
        print("✅ CrewAI with our LLM test passed")
    else:
        print("❌ CrewAI with our LLM test failed")
