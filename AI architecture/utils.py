import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import ast
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables and configure Gemini API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    pdf_reader = PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def split_text(text: str) -> List[str]:
    """Split text into smaller chunks for processing using LangChain's text splitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

def generate_summary(text: str) -> str:
    """Generate a comprehensive summary of the text using Gemini API."""
    prompt = f"""Please provide a comprehensive summary of the following text. 
    Focus on the main ideas and key points:
    
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def generate_quiz(text: str, num_questions: int = 5, difficulty: str = "intermediate") -> List[Dict]:
    """Generate quiz questions based on the text and difficulty level."""
    difficulty_prompt = {
        "beginner": "Generate beginner-level questions that test basic understanding and recall of key concepts.",
        "intermediate": "Generate intermediate-level questions that test application and analysis of concepts.",
        "advanced": "Generate advanced-level questions that test synthesis, evaluation, and complex problem-solving."
    }
    
    prompt = f"""Generate a {num_questions}-question multiple-choice quiz based on this text.
    {difficulty_prompt.get(difficulty, difficulty_prompt["intermediate"])}
    
    For each question include:
    1. A clear question
    2. Four options labeled A) through D)
    3. The correct answer letter
    4. A brief explanation

    Text to base the quiz on:
    {text}

    Respond in this exact format:
    [
      {{
        "question": "Write the question here?",
        "options": [
          "A) First option",
          "B) Second option",
          "C) Third option",
          "D) Fourth option"
        ],
        "correct_answer": "A",
        "explanation": "Explanation why this is correct"
      }}
    ]"""

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Clean up response and ensure proper format
        result = result.replace('```python', '').replace('```json', '').replace('```', '').strip()
        
        if not (result.startswith('[') and result.endswith(']')):
            raise ValueError("Response is not in the correct list format")

        # Parse the response safely
        try:
            questions = ast.literal_eval(result)
        except:
            local_dict = {}
            exec(f"quiz = {result}", {}, local_dict)
            questions = local_dict['quiz']
        
        # Validate response structure
        if not isinstance(questions, list):
            raise ValueError("Response is not a list")
        
        for q in questions:
            if not isinstance(q, dict):
                raise ValueError("Question is not a dictionary")
            if not all(key in q for key in ['question', 'options', 'correct_answer', 'explanation']):
                raise ValueError("Question missing required fields")
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                raise ValueError("Question must have exactly 4 options")
        
        return questions

    except Exception as e:
        print(f"Quiz generation error: {str(e)}")
        print(f"Raw response: {result}")
        return [{
            "question": "Failed to generate quiz questions",
            "options": [
                "A) Try generating again",
                "B) Check the text content",
                "C) Ensure text is clear",
                "D) Contact support"
            ],
            "correct_answer": "A",
            "explanation": "The AI had trouble generating questions. Please try again."
        }]

def format_quiz_for_display(quiz_questions: List[Dict]) -> str:
    """Format quiz questions for display in a readable format."""
    try:
        formatted_quiz = ""
        for i, q in enumerate(quiz_questions, 1):
            formatted_quiz += f"\nQuestion {i}:\n{q.get('question', 'Missing question')}\n\n"
            for option in q.get('options', ['No options available']):
                formatted_quiz += f"{option}\n"
            formatted_quiz += f"\nCorrect Answer: {q.get('correct_answer', 'Not available')}\n"
            formatted_quiz += f"Explanation: {q.get('explanation', 'No explanation available')}\n"
            formatted_quiz += "-" * 50 + "\n"
        return formatted_quiz
    except Exception as e:
        return f"Error formatting quiz: {str(e)}\nPlease try generating the quiz again."

def generate_practical_explanation(text: str, difficulty: str = "intermediate") -> str:
    """Generate practical explanations and examples based on the document content and difficulty level."""
    difficulty_prompt = {
        "beginner": "Provide simple, easy-to-understand explanations with basic examples. Focus on fundamental concepts and everyday applications.",
        "intermediate": "Provide detailed explanations with real-world examples. Include step-by-step processes and practical applications.",
        "advanced": "Provide in-depth explanations with complex examples. Include advanced applications, edge cases, and industry-specific implementations."
    }
    
    prompt = f"""Please provide practical explanations and examples based on the following document content.
    {difficulty_prompt.get(difficulty, difficulty_prompt["intermediate"])}
    
    Focus on:
    1. Practical applications of the concepts
    2. Real-world examples
    3. Step-by-step explanations where applicable
    4. Common use cases
    
    Document content:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def chat_with_document(text: str, question: str, difficulty: str = "intermediate") -> str:
    """Generate a response to a question about the document content with appropriate difficulty level."""
    difficulty_prompt = {
        "beginner": "Provide a simple, easy-to-understand answer. Use basic terms and everyday examples.",
        "intermediate": "Provide a detailed answer with examples. Include relevant context and explanations.",
        "advanced": "Provide an in-depth answer with technical details. Include advanced concepts and specialized applications."
    }
    
    prompt = f"""You are a helpful assistant that answers questions about the following document content.
    {difficulty_prompt.get(difficulty, difficulty_prompt["intermediate"])}
    Please provide a clear and accurate response to the question based on the information in the document.
    If the information is not available in the document, say so clearly.
    
    Document content:
    {text}
    
    Question: {question}
    """
    response = model.generate_content(prompt)
    return response.text 