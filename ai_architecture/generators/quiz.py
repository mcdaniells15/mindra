import asyncio
from typing import Dict, Any
from .base import BaseGenerator

class QuizGenerator(BaseGenerator):
    """Generator for quizzes."""

    async def generate_quiz(self, text: str, num_questions: int, difficulty: str) -> Dict[str, Any]:
        """Generate quiz with rate limiting.
        
        Args:
            text (str): The content to generate quiz from
            num_questions (int): Number of questions to generate (1-30)
            difficulty (str): Difficulty level of the quiz
            
        Returns:
            Dict containing success status and generated quiz or error
        """
        if not text:
            return {"success": False, "error": "No text provided for quiz generation"}
            
        # Validate number of questions
        if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 30:
            return {"success": False, "error": "Number of questions must be between 1 and 30"}

        try:
            # Preprocess text
            processed_text = await self._process_text(text)
            if not processed_text:
                return {"success": False, "error": "Text preprocessing failed"}

            # For larger sets of questions, we'll split into chunks to ensure quality
            max_questions_per_chunk = 10
            chunks = []
            remaining_questions = num_questions

            while remaining_questions > 0:
                questions_this_chunk = min(remaining_questions, max_questions_per_chunk)
                prompt = f"""Generate a {difficulty} level quiz with {questions_this_chunk} questions based on this content. 
For each question, provide:
A clear, specific question
Four multiple choice options (A, B, C, D)
The correct answer: A detailed explanation of why this is the correct answer

Content: {self._ensure_str(processed_text)}"""
                
                result = await self._make_api_call(prompt)
                if not result["success"]:
                    return result
                    
                chunks.append(result["content"])
                remaining_questions -= questions_this_chunk
                
                # Add a small delay between chunks to respect rate limits
                if remaining_questions > 0:
                    await asyncio.sleep(1)

            # Combine all chunks into a single quiz
            if len(chunks) == 1:
                return {"success": True, "quiz": chunks[0]}
            else:
                combined_quiz = "\n\n".join([f"Part {i+1}:\n{chunk}" for i, chunk in enumerate(chunks)])
                return {"success": True, "quiz": combined_quiz}
                
        except Exception as e:
            return {"success": False, "error": str(e)} 