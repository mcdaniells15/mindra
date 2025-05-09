from typing import Dict, Any
from ..document_processor.api_client import APIClient
from ..document_processor.text_processor import TextProcessor

class BaseGenerator:
    """Base class for all generators."""
    
    def __init__(self):
        self.api_client = APIClient()
        self.text_processor = TextProcessor()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.api_client.__aexit__(exc_type, exc_val, exc_tb)

    async def _process_text(self, text: str) -> str:
        """Process text before generation."""
        return await self.text_processor.preprocess_text(text)

    async def _make_api_call(self, prompt: str) -> Dict[str, Any]:
        """Make API call with error handling."""
        return await self.api_client.make_api_call(prompt)

    def _ensure_str(self, text: Any) -> str:
        """Ensure text is a string."""
        if isinstance(text, dict):
            if "content" in text:
                return str(text["content"])
            elif "error" in text:
                return str(text["error"])
            return str(text)
        return str(text) if text is not None else "" 