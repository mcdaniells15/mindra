from typing import Dict, Any
from .base import BaseGenerator

class ChatGenerator(BaseGenerator):
    """Generator for document chat functionality."""

    async def chat_with_document(self, text: str, question: str) -> Dict[str, Any]:
        """Chat with document with rate limiting."""
        if not question:
            return {"success": False, "error": "No question provided"}

        try:
            # Preprocess text
            processed_text = await self._process_text(text)
            if not processed_text:
                return {"success": False, "error": "Text preprocessing failed"}

            # First, try to identify if this is a general question or document-specific
            context_check_prompt = f"""Analyze if this question requires the specific document content or if it's a general topic question that can be answered with general knowledge.
            Question: {question}
            Document excerpt: {self._ensure_str(processed_text)[:500]}...

            Determine:
            1. Is this a general question about the topic?
            2. Is this specifically about the document content?
            3. What topic area does this question fall under?
            """
            
            context_result = await self._make_api_call(context_check_prompt)
            if not context_result["success"]:
                return context_result

            # Based on the context analysis, formulate the appropriate prompt
            if "general" in context_result["content"].lower():
                prompt = f"""Answer this general question about the topic: {question}

Please structure your response as follows:
1. Direct Answer
   - Provide a clear, concise answer to the question
   - Highlight key points

2. Explanation
   - Elaborate on the answer with more detail
   - Provide context and background information

3. Examples or Evidence
   - Support your answer with relevant examples
   - Cite any relevant facts or data

4. Additional Context
   - Mention any related concepts or considerations
   - Address potential follow-up questions"""
            else:
                prompt = f"""Using the following document content as context, answer this specific question: {question}

Document content:
{self._ensure_str(processed_text)}

Please structure your response as follows:
1. Direct Answer
   - Provide a clear, concise answer based on the document
   - Reference specific parts of the document

2. Supporting Evidence
   - Quote or paraphrase relevant sections
   - Explain how they support your answer

3. Context and Clarification
   - Provide any necessary background information
   - Clarify any technical terms or concepts

4. Related Information
   - Mention other relevant details from the document
   - Connect to broader themes or concepts"""

            # Make API call for the final response
            return await self._make_api_call(prompt)
            
        except Exception as e:
            return {"success": False, "error": str(e)} 