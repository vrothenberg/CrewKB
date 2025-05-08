"""
Research crew for CrewKB.

This module provides a crew for researching biomedical topics using
specialized agents and tasks.
"""

from typing import Dict, Any, Optional
from crewai import Agent, Crew, Process, Task
import yaml
import os
from pathlib import Path

from crewkb.utils.llm_factory import create_llm
from crewkb.utils.tool_factory import ToolFactory


class ResearchCrew:
    """
    Crew for researching biomedical topics.
    
    This crew uses specialized agents to research biomedical topics and
    synthesize the findings into a comprehensive knowledge base.
    """
    
    def __init__(
        self,
        topic: Optional[str] = None,
        config_dir: Optional[str] = None
    ):
        """
        Initialize the ResearchCrew.
        
        Args:
            topic: The topic to research
            config_dir: Directory containing agent and task configurations
        """
        self.topic = topic or ""
        
        # Set default config directory if not provided
        if config_dir is None:
            # Get the absolute path to the crewkb package directory
            crewkb_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            self.config_dir = os.path.join(crewkb_dir, "config")
        else:
            self.config_dir = config_dir
        
        # Load agents and tasks
        self.agents = self._load_agents()
        self.tasks = self._load_tasks()
        
        # Create crew
        self.crew = self._create_crew()
    
    def _load_agents(self) -> Dict[str, Agent]:
        """
        Load agent configurations from YAML files.
        
        Returns:
            A dictionary mapping agent names to Agent objects.
        """
        agents = {}
        agent_dir = os.path.join(self.config_dir, "agents", "research")
        
        # Check if directory exists
        if not os.path.exists(agent_dir):
            print(f"File not found: {agent_dir}")
            print(
                f"Warning: Agent config file not found at {agent_dir}. "
                f"Proceeding with empty agent configurations."
            )
            return {}
        
        # Load each agent configuration file
        for filename in os.listdir(agent_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(agent_dir, filename)
                with open(filepath, "r") as f:
                    config = yaml.safe_load(f)
                
                # Create agent
                agent_name = Path(filename).stem
                
                # Get tools for this agent using the ToolFactory
                tools = ToolFactory.create_tools_for_agent(agent_name)
                
                # Create agent
                agent = Agent(
                    role=config.get("role", ""),
                    goal=self._format_string(config.get("goal", "")),
                    backstory=config.get("backstory", ""),
                    tools=tools,
                    llm=create_llm(),
                    verbose=True
                )
                
                agents[agent_name] = agent
        
        return agents
    
    def _load_tasks(self) -> Dict[str, Task]:
        """
        Load task configurations from YAML files.
        
        Returns:
            A dictionary mapping task names to Task objects.
        """
        tasks = {}
        task_dir = os.path.join(self.config_dir, "tasks", "research")
        
        # Check if directory exists
        if not os.path.exists(task_dir):
            print(f"File not found: {task_dir}")
            print(
                f"Warning: Task config file not found at {task_dir}. "
                f"Proceeding with empty task configurations."
            )
            return {}
        
        # Load each task configuration file
        for filename in os.listdir(task_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(task_dir, filename)
                with open(filepath, "r") as f:
                    config = yaml.safe_load(f)
                
                # Get agent for this task
                agent_name = config.get("agent", "")
                if agent_name not in self.agents:
                    raise ValueError(
                        f"Agent '{agent_name}' not found for task '{filename}'"
                    )
                
                # Create task
                task_name = Path(filename).stem
                
                # Determine context based on task name
                context = []
                if task_name == "data_synthesis_task":
                    # Will be set after all tasks are created
                    pass
                
                task = Task(
                    description=self._format_string(
                        config.get("description", "")
                    ),
                    expected_output=self._format_string(
                        config.get("expected_output", "")
                    ),
                    agent=self.agents[agent_name],
                    context=context
                )
                
                tasks[task_name] = task
        
        # Set context for data_synthesis_task
        if ("data_synthesis_task" in tasks 
                and "literature_search_task" in tasks 
                and "guidelines_analysis_task" in tasks):
            tasks["data_synthesis_task"].context = [
                tasks["literature_search_task"],
                tasks["guidelines_analysis_task"]
            ]
        
        return tasks
    
    def _format_string(self, text: str) -> str:
        """
        Format a string with the topic.
        
        Args:
            text: The string to format
            
        Returns:
            The formatted string.
        """
        return text.format(topic=self.topic)
    
    def _create_crew(self) -> Crew:
        """
        Create the research crew.
        
        Returns:
            A Crew object.
        """
        # Get tasks in the correct order
        ordered_tasks = [
            self.tasks.get("literature_search_task"),
            self.tasks.get("guidelines_analysis_task"),
            self.tasks.get("data_synthesis_task")
        ]
        
        # Filter out None values
        tasks = [task for task in ordered_tasks if task is not None]
        
        # Create crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        
        return crew
    
    def run(self) -> Dict[str, Any]:
        """
        Run the research crew.
        
        Returns:
            A dictionary containing the results of each task.
        """
        # Run the crew
        results = self.crew.kickoff(inputs={"topic": self.topic})
        
        # Process results
        processed_results = {}
        
        # Extract task results
        for i, task in enumerate(self.crew.tasks):
            task_name = task.description.split("\n")[0]
            processed_results[task_name] = results[i]
        
        return processed_results
