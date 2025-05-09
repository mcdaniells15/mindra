from typing import Dict, Any
from .base import BaseGenerator

class ExplanationGenerator(BaseGenerator):
    """Generator for practical explanations."""

    async def generate_practical_explanation(self, text: str, difficulty: str) -> Dict[str, Any]:
        """Generate practical explanation with rate limiting."""
        if not text:
            return {"success": False, "error": "No text provided for explanation"}
            
        try:
            # Preprocess text
            processed_text = await self._process_text(text)
            if not processed_text:
                return {"success": False, "error": "Text preprocessing failed"}

            # Create prompt
            prompt = f"""Provide a {difficulty} level practical explanation with real-world examples for the following content:
{self._ensure_str(processed_text)}

Please structure your explanation as follows:
1. Core Concept Overview
   - Break down the main idea in simple terms
   - Explain why this concept is important

2. Real-World Examples
   - Provide 2-3 concrete, relatable examples
   - Show how the concept applies in different situations

3. Practical Applications
   - Explain how this knowledge can be used in everyday life
   - Suggest ways to implement or observe this concept

4. Common Misconceptions
   - Address any frequent misunderstandings
   - Clarify potential points of confusion

5. Key Takeaways
   - Summarize the most important points
   - Provide actionable insights"""

            # Make API call
            return await self._make_api_call(prompt)
            
        except Exception as e:
            return {"success": False, "error": str(e)} 