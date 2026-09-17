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

dalle = DallETool(
    model="dall-e-3",
    quality="standard",
    n=1,
    output_format="b64_json",
    api_key=_validate_api_key(),
    style="natural",
    image_description="create an illustration style image about {topic}"
)

@CrewBase
class CreatorsCrew():
    """CreatorsCrew crew"""
    agents_config = "config/agents_w.yaml"
    tasks_config = "config/tasks_w.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    

    @agent
    def stylist(self) -> Agent:
        return Agent(
            config=self.agents_config['stylist'], # type: ignore[index]
            knowledge_sources=[pdfs],
            verbose=True,
            max_iter=15
        )

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'], # type: ignore[index]
            verbose=True,
            llm=llm,
            max_iter=15,
            planning=False,                    # Enable plan-then-execute (default: False)
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'], # type: ignore[index]
            verbose=True,
            llm=llm,
            max_iter=15,
            planning=False,                    # Enable plan-then-execute (default: False)
        )

    @agent
    def editor(self) -> Agent:
        return Agent(
            config=self.agents_config['editor'], # type: ignore[index]
            verbose=True,
            llm=llm,
            max_iter=15
        )

    @agent
    def illustrator(self) -> Agent:
        return Agent(
        config=self.agents_config['illustrator'],
        verbose=True,
        tools=[dalle],
        llm=llm,
            max_iter=15
    )

    @task
    def stylist_task(self) -> Task:
        return Task(
            config=self.tasks_config['stylist_task'], # type: ignore[index]
            output_file='style.md'
        )

    @task
    def planner_task(self) -> Task:
        return Task(
            config=self.tasks_config['planner_task'], # type: ignore[index]
            output_file='plan.md'
        )

    @task
    def writer_task(self) -> Task:
        return Task(
            config=self.tasks_config['writer_task'], # type: ignore[index]
            output_file='article.md'
        )

    @task
    def illustrate(self) -> Task:
        return Task(
        config=self.tasks_config['illustrate'],
        output_file='output/picture.txt' # This is the file that will contain the link to the picture's.
        )

    @task
    def editor_task(self) -> Task:
        return Task(
            config=self.tasks_config['editor_task'], # type: ignore[index]
            output_file='final_article.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Creators crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
