from typing import List, Dict, Any
import google.generativeai as genai
from ..config.config import Config
import asyncio
from ..core.cache import response_cache
from ..exceptions import (
    DocumentProcessingError,
    APIError,
    RateLimitError,
    ValidationError
)
from .file_handlers import FileHandler
from .text_processor import TextProcessor
from .api_client import APIClient
from ..generators import (
    SummaryGenerator,
    QuizGenerator,
    ExplanationGenerator,
    ChatGenerator
)

# Configure Gemini API
genai.configure(api_key=Config.API_KEY)

class DocumentProcessor:
    """Main document processing class that integrates all components."""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.text_processor = TextProcessor()
        self.api_client = None  # Initialize as None
        self.summary_generator = None
        self.quiz_generator = None
        self.explanation_generator = None
        self.chat_generator = None
        self.batch_size = Config.BATCH_PROCESSING["default_batch_size"]
        self.batch_delay = Config.BATCH_PROCESSING["batch_delay"]

    async def __aenter__(self):
        """Async context manager entry."""
        # Initialize components with proper session management
        self.api_client = APIClient()
        await self.api_client.__aenter__()
        
        self.summary_generator = SummaryGenerator()
        await self.summary_generator.__aenter__()
        
        self.quiz_generator = QuizGenerator()
        await self.quiz_generator.__aenter__()
        
        self.explanation_generator = ExplanationGenerator()
        await self.explanation_generator.__aenter__()
        
        self.chat_generator = ChatGenerator()
        await self.chat_generator.__aenter__()
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        # Close all sessions in reverse order
        if self.chat_generator:
            await self.chat_generator.__aexit__(exc_type, exc_val, exc_tb)
        if self.explanation_generator:
            await self.explanation_generator.__aexit__(exc_type, exc_val, exc_tb)
        if self.quiz_generator:
            await self.quiz_generator.__aexit__(exc_type, exc_val, exc_tb)
        if self.summary_generator:
            await self.summary_generator.__aexit__(exc_type, exc_val, exc_tb)
        if self.api_client:
            await self.api_client.__aexit__(exc_type, exc_val, exc_tb)

    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document with optimized parallel processing and rate limiting."""
        try:
            if not file_path:
                raise ValidationError("No file path provided", field="file_path", value=file_path)

            # Extract and preprocess text
            try:
                text = await self.file_handler.extract_text_from_file(file_path)
                if not text:
                    raise DocumentProcessingError(
                        "Could not extract text from document",
                        file_path=file_path,
                        stage="text_extraction"
                    )
            except Exception as e:
                raise DocumentProcessingError(
                    f"Error during text extraction: {str(e)}",
                    file_path=file_path,
                    stage="text_extraction",
                    details={"original_error": str(e)}
                )

            try:
                text = await self.text_processor.preprocess_text(text)
                if not text:
                    raise DocumentProcessingError(
                        "Document contains no valid text after preprocessing",
                        file_path=file_path,
                        stage="preprocessing"
                    )
            except Exception as e:
                raise DocumentProcessingError(
                    f"Error during text preprocessing: {str(e)}",
                    file_path=file_path,
                    stage="preprocessing",
                    details={"original_error": str(e)}
                )

            # Create and process chunks
            try:
                chunks = await self.text_processor.create_smart_chunks(text)
                if not chunks:
                    raise DocumentProcessingError(
                        "Could not create valid chunks from document",
                        file_path=file_path,
                        stage="chunking"
                    )
            except Exception as e:
                raise DocumentProcessingError(
                    f"Error during text chunking: {str(e)}",
                    file_path=file_path,
                    stage="chunking",
                    details={"original_error": str(e)}
                )

            results = await self._process_chunks_in_batches(chunks)
            
            # Add more detailed error information for debugging
            if not results:
                details = {
                    "chunks_count": len(chunks),
                    "file_path": file_path,
                    "text_length": len(text) if text else 0,
                }
                raise DocumentProcessingError(
                    "No valid content generated from document - all chunks failed processing",
                    file_path=file_path,
                    stage="content_generation",
                    details=details
                )
            
            processed_content = " ".join(results)
            if not processed_content.strip():
                details = {
                    "results_count": len(results),
                    "chunks_count": len(chunks),
                    "file_path": file_path,
                }
                raise DocumentProcessingError(
                    "Generated content is empty after joining results",
                    file_path=file_path,
                    stage="content_generation",
                    details=details
                )
            
            return {
                "success": True,
                "content": processed_content,
                "metadata": {
                    "file_name": file_path,
                    "chunk_count": len(chunks),
                    "processed_chunks": len(results),
                    "processing_stats": {
                        "chunks_per_batch": self.batch_size,
                        "total_batches": (len(chunks) + self.batch_size - 1) // self.batch_size,
                        "content_length": len(processed_content),
                        "batch_settings": {
                            "batch_size": self.batch_size,
                            "chunk_size": self.text_processor.chunk_size,
                            "chunk_overlap": self.text_processor.overlap,
                            "batch_delay": self.batch_delay
                        }
                    }
                }
            }
        except (DocumentProcessingError, APIError, RateLimitError, ValidationError) as e:
            return {"success": False, "error": str(e), "details": e.details if hasattr(e, 'details') else {}}
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "details": {"type": type(e).__name__}
            }

    async def _process_chunks_in_batches(self, chunks: List[str], batch_size: int = None) -> List[str]:
        """Process chunks in batches to optimize API usage."""
        results = []
        failed_chunks = []
        
        # Use provided batch_size or default from config
        batch_size = min(
            max(
                batch_size or self.batch_size,
                Config.BATCH_PROCESSING["min_batch_size"]
            ),
            Config.BATCH_PROCESSING["max_batch_size"]
        )
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [self._process_chunk(chunk) for chunk in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle batch results
            for chunk, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    failed_chunks.append((chunk, str(result)))
                elif result:
                    results.append(result)
            
            # Add configurable delay between batches to respect rate limits
            if i + batch_size < len(chunks):
                await asyncio.sleep(self.batch_delay)
        
        # If we have no results but have failed chunks, raise an error with details
        if not results and failed_chunks:
            raise DocumentProcessingError(
                "All chunks failed to process",
                stage="batch_processing",
                details={
                    "failed_chunks_count": len(failed_chunks),
                    "total_chunks": len(chunks),
                    "first_failure": failed_chunks[0][1] if failed_chunks else None,
                    "batch_size": batch_size
                }
            )
                
        return results

    async def _process_chunk(self, chunk: str) -> str:
        """Process a single chunk of text using the API."""
        if not chunk or not chunk.strip():
            return ""
            
        # Check cache first
        cached_result = response_cache.get(chunk)
        if cached_result:
            return cached_result

        try:
            # Make API call if not in cache using existing client
            result = await self.api_client.make_api_call(chunk)
            if result.get("success") and result.get("content"):
                content = result["content"].strip()
                if content:
                    response_cache.set(chunk, content)
                    return content
            return ""
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to process chunk: {str(e)}",
                stage="chunk_processing",
                details={"chunk_length": len(chunk)}
            )

    async def generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate summary using the summary generator."""
        return await self.summary_generator.generate_summary(text)

    async def generate_quiz(self, text: str, num_questions: int, difficulty: str) -> Dict[str, Any]:
        """Generate quiz using the quiz generator."""
        return await self.quiz_generator.generate_quiz(text, num_questions, difficulty)

    async def generate_practical_explanation(self, text: str, difficulty: str) -> Dict[str, Any]:
        """Generate practical explanation using the explanation generator."""
        return await self.explanation_generator.generate_practical_explanation(text, difficulty)

    async def chat_with_document(self, text: str, question: str) -> Dict[str, Any]:
        """Chat with document using the chat generator."""
        return await self.chat_generator.chat_with_document(text, question) 