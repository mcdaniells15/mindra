import asyncio
from typing import List
from ..config.config import Config


class TextProcessor:
    """Class for text processing operations."""
    
    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or Config.BATCH_PROCESSING["chunk_size"]
        self.overlap = overlap or Config.BATCH_PROCESSING["chunk_overlap"]

    async def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text before sending to API."""
        if not text:
            return ""
            
        # Run CPU-intensive text processing in a thread pool
        loop = asyncio.get_event_loop()
        
        def process():
            # Remove redundant whitespace
            text_clean = " ".join(text.split())
            # Remove common headers/footers patterns
            text_clean = text_clean.replace("Page 1 of", "").replace("Confidential", "")
            return text_clean.strip()

        try:
            result = await loop.run_in_executor(None, process)  
            return result
        except Exception as e:
            
            return text.strip()

    async def create_smart_chunks(self, text: str) -> List[str]:
        """Create overlapping chunks of text that preserve context."""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)

        async def process_chunk(start_pos, end_pos):
            """Process a single chunk of text."""
            if end_pos >= text_length:
                chunk = text[start_pos:].strip()
                return chunk if chunk else None
                
            # Try to find a good breaking point (end of sentence)
            break_point = text.rfind('. ', start_pos + self.chunk_size - self.overlap, end_pos)
            if break_point != -1:
                end_pos = break_point + 1
            
            chunk = text[start_pos:end_pos].strip()
            return chunk if chunk else None

        try:
            while start < text_length:
                end = start + self.chunk_size
                chunk = await process_chunk(start, end)
                
                if chunk:
                    chunks.append(chunk)
                if end >= text_length:
                    break
                    
                start = end - self.overlap

            
            return chunks
        except Exception as e:
           
            # Fallback to simple chunking if smart chunking fails
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.overlap)] 