"""
ContentCreationCrew for creating knowledge base article content.

This module provides a crew that uses content creation agents to create
content for knowledge base articles based on research findings.
"""

from typing import Dict, Any, Optional
from crewai import Crew, Process, Agent, Task
import yaml
import os
from pathlib import Path

from crewkb.utils.llm_factory import create_llm


class ContentCreationCrew:
    """
    Crew for creating knowledge base article content.
    
    This crew uses content creation agents to create content for
    knowledge base articles based on research findings.
    """
    
    def __init__(
        self,
        article_type: str,
        topic: str,
        research_data: str,
        config_dir: Optional[str] = None
    ):
        """
        Initialize the ContentCreationCrew.
        
        Args:
            article_type: The type of article (disease, biomarker, or lab test)
            topic: The topic of the article
            research_data: The research data to use for content creation
            config_dir: Directory containing agent and task configurations
        """
        self.article_type = article_type
        self.topic = topic
        self.research_data = research_data
        
        # Set default config directory if not provided
        if config_dir is None:
            self.config_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config"
            )
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
        agent_dir = os.path.join(self.config_dir, "agents", "content")
        
        # Check if directory exists
        if not os.path.exists(agent_dir):
            raise FileNotFoundError(f"Agent directory not found: {agent_dir}")
        
        # Load each agent configuration file
        for filename in os.listdir(agent_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(agent_dir, filename)
                with open(filepath, "r") as f:
                    config = yaml.safe_load(f)
                
                # Create agent
                agent_name = Path(filename).stem
                agent = Agent(
                    role=config.get("role", ""),
                    goal=self._format_string(config.get("goal", "")),
                    backstory=config.get("backstory", ""),
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
        task_dir = os.path.join(self.config_dir, "tasks", "content")
        
        # Check if directory exists
        if not os.path.exists(task_dir):
            raise FileNotFoundError(f"Task directory not found: {task_dir}")
        
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
                task = Task(
                    description=self._format_string(
                        config.get("description", "")
                    ),
                    expected_output=self._format_string(
                        config.get("expected_output", "")
                    ),
                    agent=self.agents[agent_name],
                    context=self._get_context(config.get("context", []))
                )
                
                tasks[task_name] = task
        
        return tasks
    
    def _format_string(self, text: str) -> str:
        """
        Format a string with article type and topic.
        
        Args:
            text: The string to format
            
        Returns:
            The formatted string.
        """
        return text.format(
            article_type=self.article_type,
            topic=self.topic
        )
    
    def _get_context(self, context_tasks: list) -> list:
        """
        Get context from previous tasks.
        
        Args:
            context_tasks: List of task names to use as context
            
        Returns:
            A list of task objects to use as context.
        """
        context = []
        
        # Add research data as context
        context.append(f"Research Data:\n\n{self.research_data}")
        
        # Add tasks as context
        for task_name in context_tasks:
            if task_name in self.tasks:
                context.append(self.tasks[task_name])
        
        return context
    
    def _create_crew(self) -> Crew:
        """
        Create the content creation crew.
        
        Returns:
            A Crew object.
        """
        # Get tasks in the correct order
        ordered_tasks = [
            self.tasks.get("content_planning_task"),
            self.tasks.get("content_writing_task"),
            self.tasks.get("citation_management_task")
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
        Run the content creation crew.
        
        Returns:
            A dictionary containing the results of each task.
        """
        # Run the crew
        results = self.crew.kickoff()
        
        # Process results
        processed_results = {}
        
        # Extract task results
        for i, task in enumerate(self.crew.tasks):
            task_name = task.description.split("\n")[0]
            processed_results[task_name] = results[i]
        
        return processed_results
