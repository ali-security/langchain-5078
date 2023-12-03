from pathlib import Path
from typing import List

from langchain_core.documents import Document

from langchain_integrations.document_loaders.base import BaseLoader


class NotionDirectoryLoader(BaseLoader):
    """Load `Notion directory` dump."""

    def __init__(self, path: str, *, encoding: str = "utf-8") -> None:
        """Initialize with a file path."""
        self.file_path = path
        self.encoding = encoding

    def load(self) -> List[Document]:
        """Load documents."""
        paths = list(Path(self.file_path).glob("**/*.md"))
        docs = []
        for p in paths:
            with open(p, encoding=self.encoding) as f:
                text = f.read()
            metadata = {"source": str(p)}
            docs.append(Document(page_content=text, metadata=metadata))
        return docs
