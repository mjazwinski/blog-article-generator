from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource

from crewai_tools import SerperDevTool, DallETool
from dotenv import dotenv_values, load_dotenv
import os
from pathlib import Path

PACKAGE_ENV_PATH = Path(__file__).with_name(".env")
PROJECT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=PACKAGE_ENV_PATH, override=False)
load_dotenv(dotenv_path=PROJECT_ENV_PATH, override=False)
PACKAGE_ENV_VALUES = dotenv_values(PACKAGE_ENV_PATH)
PROJECT_ENV_VALUES = dotenv_values(PROJECT_ENV_PATH)


def _is_valid_candidate(api_key: str) -> bool:
    return bool(api_key) and api_key not in {"123", "your_openai_api_key"} and api_key.startswith("sk-")


def _validate_api_key() -> str:
    process_key = os.environ.get("OPENAI_API_KEY", "").strip()
    package_key = str(PACKAGE_ENV_VALUES.get("OPENAI_API_KEY", "")).strip()
    project_key = str(PROJECT_ENV_VALUES.get("OPENAI_API_KEY", "")).strip()
    selected_api_key = ""
    for candidate in [process_key, package_key, project_key]:
        if _is_valid_candidate(candidate):
            selected_api_key = candidate
            break
    if not selected_api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing, placeholder, or malformed. "
            "Set a valid key in the package .env or your process environment."
        )
    os.environ["OPENAI_API_KEY"] = selected_api_key
    return selected_api_key

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


pdfs = PDFKnowledgeSource(
    file_paths=['article1.pdf',
                'article2.pdf',
                'article3.pdf'
                ]
)

llm = LLM(
    # model="groq/qwen-qwq-32b",
    # api_key= os.environ.get("GROQ_API_KEY"),
    model= os.environ.get("MODEL"),
    api_key=_validate_api_key(),
    temperature=0.4
)

fllm = LLM(
    # model="groq/qwen-qwq-32b",
    # api_key= os.environ.get("GROQ_API_KEY"),
    model= "openai/gpt-4o-mini",
    api_key=_validate_api_key(),
    temperature=0.4
)


@CrewBase
class ReaserchersCrew():
    """ReaserchersCrew crew"""
    agents_config = "config/agents_r.yaml"
    tasks_config = "config/tasks_r.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        serper_api_key = os.environ.get("SERPER_API_KEY", "").strip()
        researcher_tools = [SerperDevTool()] if serper_api_key else []
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            tools=researcher_tools,
            verbose=True,
            llm=llm,
            function_calling_llm=fllm,
            max_iter=15
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

 
    @crew
    def crew(self) -> Crew:
        """Creates the Reaseracher crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
