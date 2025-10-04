from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
import datetime
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class CrewPythonGameBuilder():
    """CrewPythonGameBuilder crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self, game_name: str = None):
        """Initialize the crew with an optional game name for folder organization"""
        super().__init__()
        self.game_name = game_name or f"game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_folder = f"output/{self.game_name}"
        
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def senior_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_engineer_agent'], # type: ignore[index]
            allow_delegation=False,
            verbose=True
        )
    
    @agent
    def qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_engineer_agent'], # type: ignore[index]
            allow_delegation=False,
            verbose=True
        )
    
    @agent
    def chief_qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['chief_qa_engineer_agent'], # type: ignore[index]
            allow_delegation=True,
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'], # type: ignore[index]
            agent=self.senior_engineer_agent(),
            output_file=f'{self.output_folder}/generated_game.py'
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'], # type: ignore[index]
            agent=self.qa_engineer_agent(),
            output_file=f'{self.output_folder}/code_review.md'
        )

    @task
    def evaluate_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_task'], # type: ignore[index]
            agent=self.chief_qa_engineer_agent(),
            output_file=f'{self.output_folder}/final_evaluation.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewPythonGameBuilder crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
