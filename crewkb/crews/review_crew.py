"""
ReviewCrew for reviewing knowledge base article content.

This module provides a crew that uses review agents to evaluate and improve
knowledge base articles for accuracy, readability, and patient relevance.
"""

from typing import Dict, Any, Optional, List
from crewai import Crew, Process, Agent, Task
import yaml
import os
from pathlib import Path

from crewkb.utils.llm_factory import create_llm
from crewkb.utils.tool_factory import ToolFactory


class ReviewCrew:
    """
    Crew for reviewing knowledge base article content.
    
    This crew uses specialized review agents to evaluate and improve
    knowledge base articles for accuracy, readability, and patient relevance.
    It can also detect and resolve conflicts between different review
    perspectives.
    """
    
    def __init__(
        self,
        article_type: str,
        topic: str,
        content: str,
        config_dir: Optional[str] = None
    ):
        """
        Initialize the ReviewCrew.
        
        Args:
            article_type: The type of article (disease, biomarker, or lab test)
            topic: The topic of the article
            content: The article content to review
            config_dir: Directory containing agent and task configurations
        """
        self.article_type = article_type
        self.topic = topic
        self.content = content
        
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
    
    def _load_agents(self) -> Dict[str, Agent]:
        """
        Load agent configurations from YAML files.
        
        Returns:
            A dictionary mapping agent names to Agent objects.
        """
        agents = {}
        agent_dir = os.path.join(self.config_dir, "agents", "review")
        
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
                
                # Get tools for this agent
                tools = ToolFactory.create_tools_for_agent(agent_name)
                
                # Create agent with tools
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
        task_dir = os.path.join(self.config_dir, "tasks", "review")
        
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
                    description=self._format_string(config.get("description", "")),
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
        
        # Add article content as context
        context.append(f"Article Content:\n\n{self.content}")
        
        # Add tasks as context
        for task_name in context_tasks:
            if task_name in self.tasks:
                context.append(self.tasks[task_name])
        
        return context
    
    def _detect_conflicts(self, review_results: List[str]) -> Dict[str, Any]:
        """
        Detect conflicts in the review results.
        
        Args:
            review_results: List of review results from different agents
            
        Returns:
            A dictionary containing detected conflicts.
        """
        # This is a simplified implementation
        # In a real implementation, this would use NLP to identify
        # contradictory recommendations
        
        conflicts = {}
        
        # Extract recommendations from each review
        accuracy_recommendations = self._extract_recommendations(review_results[0])
        content_recommendations = self._extract_recommendations(review_results[1])
        patient_recommendations = self._extract_recommendations(review_results[2])
        
        # Check for potential conflicts between accuracy and readability
        for acc_rec in accuracy_recommendations:
            for cont_rec in content_recommendations:
                if self._are_conflicting(acc_rec, cont_rec):
                    conflicts.setdefault("accuracy_vs_readability", []).append({
                        "accuracy": acc_rec,
                        "readability": cont_rec
                    })
        
        # Check for potential conflicts between accuracy and patient perspective
        for acc_rec in accuracy_recommendations:
            for pat_rec in patient_recommendations:
                if self._are_conflicting(acc_rec, pat_rec):
                    conflicts.setdefault("accuracy_vs_patient", []).append({
                        "accuracy": acc_rec,
                        "patient": pat_rec
                    })
        
        # Check for potential conflicts between readability and patient perspective
        for cont_rec in content_recommendations:
            for pat_rec in patient_recommendations:
                if self._are_conflicting(cont_rec, pat_rec):
                    conflicts.setdefault("readability_vs_patient", []).append({
                        "readability": cont_rec,
                        "patient": pat_rec
                    })
        
        return conflicts
    
    def _extract_recommendations(self, review_result: str) -> List[str]:
        """
        Extract recommendations from a review result.
        
        Args:
            review_result: The review result to extract recommendations from
            
        Returns:
            A list of recommendations.
        """
        # This is a simplified implementation
        # In a real implementation, this would use NLP to extract
        # structured recommendations
        
        recommendations = []
        
        # Look for recommendation sections
        if "Recommendations:" in review_result:
            rec_section = review_result.split("Recommendations:")[1]
            # Extract individual recommendations
            for line in rec_section.split("\n"):
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*") or 
                             (line[0].isdigit() and line[1] == ".")):
                    recommendations.append(line[2:].strip())
        
        return recommendations
    
    def _are_conflicting(self, rec1: str, rec2: str) -> bool:
        """
        Check if two recommendations are potentially conflicting.
        
        Args:
            rec1: First recommendation
            rec2: Second recommendation
            
        Returns:
            True if the recommendations are potentially conflicting, False otherwise.
        """
        # This is a simplified implementation
        # In a real implementation, this would use NLP to identify
        # semantic contradictions
        
        # Check for opposite directives
        opposite_pairs = [
            ("simplify", "add more detail"),
            ("remove", "add"),
            ("shorten", "expand"),
            ("technical", "simple"),
            ("formal", "conversational")
        ]
        
        for term1, term2 in opposite_pairs:
            if term1 in rec1.lower() and term2 in rec2.lower():
                return True
            if term2 in rec1.lower() and term1 in rec2.lower():
                return True
        
        return False
    
    def run(self) -> Dict[str, Any]:
        """
        Run the review crew.
        
        Returns:
            A dictionary containing the results of each task and conflict resolution.
        """
        # Create sequential review crew
        review_crew = Crew(
            agents=[
                self.agents.get("medical_accuracy_reviewer"),
                self.agents.get("medical_content_editor"),
                self.agents.get("patient_perspective_reviewer")
            ],
            tasks=[
                self.tasks.get("accuracy_review_task"),
                self.tasks.get("content_editing_task"),
                self.tasks.get("patient_perspective_task")
            ],
            verbose=True,
            process=Process.sequential
        )
        
        # Run the review crew
        review_results = review_crew.kickoff()
        
        # Process results
        processed_results = {}
        
        # Extract task results
        for i, task in enumerate(review_crew.tasks):
            task_name = task.description.split("\n")[0]
            processed_results[task_name] = review_results[i]
        
        # Detect conflicts
        conflicts = self._detect_conflicts([
            review_results[0],
            review_results[1],
            review_results[2]
        ])
        
        # If conflicts are detected, use the manager agent to resolve them
        if conflicts:
            # Create conflict resolution crew
            resolution_crew = Crew(
                agents=[self.agents.get("review_manager")],
                tasks=[self.tasks.get("conflict_resolution_task")],
                verbose=True,
                process=Process.sequential
            )
            
            # Add conflicts to the context
            resolution_context = {
                "article_content": self.content,
                "accuracy_review": review_results[0],
                "content_editing": review_results[1],
                "patient_perspective": review_results[2],
                "conflicts": conflicts
            }
            
            # Run the conflict resolution crew
            resolution_result = resolution_crew.kickoff(inputs=resolution_context)
            
            # Add resolution result to processed results
            processed_results["conflict_resolution"] = resolution_result[0]
        
        return processed_results
