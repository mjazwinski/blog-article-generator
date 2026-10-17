from pathlib import Path

from crewai.project import load_crew


def get_crew():
    return load_crew(Path(__file__).with_name("crew.jsonc"))
