import os
import asyncio
import fitz
from docx import Document
from pptx import Presentation
from typing import List
from .base import DocumentProcessingError

class FileHandler:
    """Base class for file handling operations."""
    
    @staticmethod
    async def extract_text_from_file(file_path: str) -> str:
        """Extract text from various file formats with proper error handling."""
        try:
            if not file_path:
                raise ValueError("No file path provided")
                
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            if not os.path.isfile(file_path):
                raise ValueError(f"Path is not a file: {file_path}")
                
            if os.path.getsize(file_path) == 0:
                raise ValueError(f"File is empty: {file_path}")
                
            if file_extension == '.pdf':
                return await PDFHandler.extract_text(file_path)
            elif file_extension in ['.docx', '.doc']:
                return await DOCXHandler.extract_text(file_path)
            elif file_extension in ['.pptx', '.ppt']:
                return await PPTXHandler.extract_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}. Supported formats are: PDF (.pdf), Word (.doc, .docx), PowerPoint (.ppt, .pptx)")
        except Exception as e:
            error_msg = f"Failed to extract text from file: {str(e)}"
            if isinstance(e, (FileNotFoundError, ValueError)):
                error_msg = str(e)
            raise DocumentProcessingError(error_msg, file_path=file_path)

class PDFHandler:
    """Handler for PDF file operations."""
    
    @staticmethod
    async def extract_text(file_path: str) -> str:
        """Extract text from PDF using PyMuPDF with proper error handling."""
        try:
            # Open the PDF file
            doc = fitz.open(file_path)
            
            async def process_page(page) -> str:
                """Process a single page asynchronously."""
                try:
                    # Get text with improved formatting and layout preservation
                    text = page.get_text("text", sort=True)
                    if text:
                        # Clean up the text
                        text = text.strip()
                        # Remove redundant whitespace while preserving paragraph breaks
                        return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())
                    return ""
                except Exception:
                    return "Failed to process page"

            # Create tasks for processing all pages concurrently
            tasks = [process_page(page) for page in doc]
            text_parts = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Close the document after processing
            doc.close()
            
            # Handle any exceptions from gather
            processed_parts = []
            for result in text_parts:
                if isinstance(result, Exception):
                    continue
                if result:
                    processed_parts.append(result)
            
            if not processed_parts:
                raise DocumentProcessingError("No text could be extracted from the PDF")
            
            return "\n\n".join(processed_parts).strip()
        except Exception as e:
            raise DocumentProcessingError(f"Failed to extract text from PDF: {str(e)}")

class DOCXHandler:
    """Handler for DOCX file operations."""
    
    @staticmethod
    async def extract_text(file_path: str) -> str:
        """Extract text from DOCX file asynchronously with proper error handling."""
        try:
            loop = asyncio.get_event_loop()
            # Run CPU-bound document processing in a thread pool
            doc = await loop.run_in_executor(None, Document, file_path)
            
            async def process_paragraph(para) -> str:
                """Process a single paragraph asynchronously."""
                try:
                    return para.text.strip() if para.text.strip() else ""
                except Exception:
                    return "Failed to extract text"

            # Process paragraphs concurrently
            tasks = [process_paragraph(para) for para in doc.paragraphs]
            text_parts = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions from gather
            processed_parts = []
            for result in text_parts:
                if isinstance(result, Exception):
                    continue
                if result:
                    processed_parts.append(result)

            if not processed_parts:
                raise DocumentProcessingError("No text could be extracted from the DOCX file")

            return " ".join(processed_parts)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to extract text from DOCX: {str(e)}")

class PPTXHandler:
    """Handler for PPTX file operations."""
    
    @staticmethod
    async def extract_text(file_path: str) -> str:
        """Extract text from PPTX file asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            # Run CPU-bound presentation processing in a thread pool
            prs = await loop.run_in_executor(None, Presentation, file_path)
            text_parts = []
            
            async def process_shape(shape):
                if hasattr(shape, "text") and shape.text.strip():
                    return shape.text.strip()
                return ""

            for slide in prs.slides:
                # Process shapes concurrently within each slide
                shape_tasks = [process_shape(shape) for shape in slide.shapes]
                shape_texts = await asyncio.gather(*shape_tasks)
                text_parts.extend(text for text in shape_texts if text)
                
            return " ".join(text_parts)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to extract text from PPTX: {str(e)}") 