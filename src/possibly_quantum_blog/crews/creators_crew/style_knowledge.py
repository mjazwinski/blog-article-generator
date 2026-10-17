from pathlib import Path

from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.utilities.constants import KNOWLEDGE_DIRECTORY

# PDFKnowledgeSource resolves file names against KNOWLEDGE_DIRECTORY relative to the
# working directory, so the crew must be run from the project root.
style_examples = PDFKnowledgeSource(
    file_paths=sorted(pdf.name for pdf in Path(KNOWLEDGE_DIRECTORY).glob("*.pdf"))
)
