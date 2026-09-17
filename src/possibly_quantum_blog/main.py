#!/usr/bin/env python
import argparse
import warnings
from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start
from datetime import datetime
from possibly_quantum_blog.creators_crew import CreatorsCrew as creators_crew  # type: ignore
from possibly_quantum_blog.researchers_crew import ReaserchersCrew as researchers_crew  # type: ignore

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

class BlogArticleFlowState(BaseModel):
  topic: str = "Quantum anything"
  current_year: str = str(datetime.now().year)
  output: str = str(datetime.now().date)+"_article"
  research_data: str = ""


class PossiblyQuantumBlogFlow(Flow[BlogArticleFlowState]):
    """Flow for creating a comprehensive guide on any topic"""
    @start()
    def startReasearch(self):
        """
        Run the crew.
        """
        self.state.topic = input("What topic would you like to create a guide for? ")
        #parser = argparse.ArgumentParser(description="Run the ArtificeBlog crew")
        #parser.add_argument("--topic", required=True, help="Article topic")
        #args = parser.parse_args()
        #print(f"topic {args.topic}")

        inputs = {
            'topic': self.state.topic,
            'current_year': str(datetime.now().year),
            'output': str(datetime.now().date)+"_article"
        }

        try:
            result =researchers_crew().crew().kickoff(inputs=inputs)
            self.state.research_data = result.raw
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    @listen(startReasearch)
    def writeArticle(self):

        inputs = {
            'topic': self.state.topic,
            'current_year': str(datetime.now().year),
            'output': str(datetime.now().date)+"_article",
            'research_data': self.state.research_data
        }

        try:
            creators_crew().crew().kickoff(inputs=inputs)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")
        
def kickoff():
  PossiblyQuantumBlogFlow().kickoff()


def plot():
  PossiblyQuantumBlogFlow().plot()

def run():
  PossiblyQuantumBlogFlow().kickoff()

if __name__ == "__main__":
  kickoff()