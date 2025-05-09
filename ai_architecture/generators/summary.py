from typing import Dict, Any
from .base import BaseGenerator

class SummaryGenerator(BaseGenerator):
    """Generator for text summaries."""

    async def generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate summary with rate limiting."""
        if not text:
            return {"success": False, "error": "No text provided for summarization"}
            
        try:
            # Preprocess text
            processed_text = await self._process_text(text)
            if not processed_text:
                return {"success": False, "error": "Text preprocessing failed"}

            # Create prompt
            prompt = """Please provide a detailed and structured summary of the following text. 
Follow this format:

1. MAIN POINTS:
- List the 3-5 most important points
- Explain each point briefly but clearly

2. KEY CONCEPTS:
- Identify and explain the main concepts discussed
- Show how they relate to each other

3. DETAILED EXPLANATION:
- Provide a thorough explanation of the content
- Include relevant examples or evidence
- Explain the significance of each point

4. CONCLUSION:
- Summarize the overall message
- Highlight the most important takeaways
- Explain the practical implications """ + self._ensure_str(processed_text)

            # Make API call
            return await self._make_api_call(prompt)
            
        except Exception as e:
            return {"success": False, "error": str(e)} 