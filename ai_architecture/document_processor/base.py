import asyncio
import nest_asyncio
from typing import Any
from ..exceptions import DocumentProcessingError, APIError

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

async def get_or_create_event_loop():
    """Get or create an event loop with proper error handling."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    except Exception as e:
        raise DocumentProcessingError(
            f"Failed to initialize event loop",
            stage="event_loop_initialization",
            details={"original_error": str(e)}
        )

class BaseDocumentProcessor:
    """Base class for document processing functionality."""
    
    def __init__(self):
        self.loop = None
        asyncio.run(self._setup_event_loop())

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    async def _setup_event_loop(self):
        """Setup event loop for the processor with proper error handling."""
        try:
            self.loop = await get_or_create_event_loop()
        except Exception as e:
            raise DocumentProcessingError(
                "Failed to setup event loop",
                stage="event_loop_setup",
                details={"original_error": str(e)}
            )

    def _ensure_str(self, text: Any) -> str:
        """Ensure the input is converted to a string safely with proper error handling."""
        try:
            if isinstance(text, dict):
                if "content" in text:
                    return str(text["content"])
                elif "error" in text:
                    return str(text["error"])
                return str(text)
            return str(text) if text is not None else ""
        except Exception:
            return ""

    async def _run_async(self, coro):
        """Run coroutine in the processor's event loop with proper error handling."""
        try:
            if asyncio.get_event_loop() != self.loop:
                asyncio.set_event_loop(self.loop)
            return await coro
        except Exception as e:
            raise DocumentProcessingError(
                "Failed to run async operation",
                stage="async_execution",
                details={"original_error": str(e)}
            )

    async def run_async(self, coro):
        """Run a coroutine synchronously with proper error handling."""
        try:
            if not self.loop or self.loop.is_closed():
                await self._setup_event_loop()
            return await self._run_async(coro)
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                await self._setup_event_loop()
                return await self._run_async(coro)
            raise DocumentProcessingError(
                "Failed to run async operation",
                stage="async_execution",
                details={"error_type": "RuntimeError", "original_error": str(e)}
            )
        except Exception as e:
            raise DocumentProcessingError(
                "Failed to run async operation",
                stage="async_execution",
                details={"original_error": str(e)}
            ) 