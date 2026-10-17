#!/usr/bin/env python
import warnings
from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start
from datetime import datetime
from possibly_quantum_blog.crews.creators_crew.creators_crew import get_crew as get_creators_crew  # type: ignore
from possibly_quantum_blog.crews.reaserchers_crew.researcher_crew import get_crew as get_researchers_crew  # type: ignore
from possibly_quantum_blog.env import load_environment

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
load_environment()


class BlogArticleFlowState(BaseModel):
    topic: str = "Quantum anything"
    current_year: str = str(datetime.now().year)
    output: str = str(datetime.now().date) + "_article"
    research_data: str = ""


class PossiblyQuantumBlogFlow(Flow[BlogArticleFlowState]):
    """Flow for creating a comprehensive guide on any topic"""

    @start()
    def startReasearch(self):
        """Gather the topic then run the researchers crew."""
        self.state.topic = input("What topic would you like to create a guide for? ")

        inputs = {
            "topic": self.state.topic,
            "current_year": str(datetime.now().year),
            "output": str(datetime.now().date) + "_article",
        }

        try:
            crew, default_inputs = get_researchers_crew()
            result = crew.kickoff(inputs={**default_inputs, **inputs})
            self.state.research_data = result.raw
        except Exception as e:
            raise Exception(f"An error occurred while running the researchers crew: {e}")

    @listen(startReasearch)
    def writeArticle(self):
        """Run the creators crew with the research gathered above."""
        inputs = {
            "topic": self.state.topic,
            "current_year": str(datetime.now().year),
            "output": str(datetime.now().date) + "_article",
            "research_data": self.state.research_data,
        }

        try:
            crew, default_inputs = get_creators_crew()
            crew.kickoff(inputs={**default_inputs, **inputs})
        except Exception as e:
            raise Exception(f"An error occurred while running the creators crew: {e}")


def kickoff():
    PossiblyQuantumBlogFlow().kickoff()


def plot():
    PossiblyQuantumBlogFlow().plot()


def run():
    PossiblyQuantumBlogFlow().kickoff()


if __name__ == "__main__":
    kickoff()
