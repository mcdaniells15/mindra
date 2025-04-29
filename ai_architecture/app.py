import streamlit as st
import os
import asyncio
from utils import (
    extract_text_from_file,
    split_text,
    generate_summary,
    generate_quiz,
    format_quiz_for_display,
    chat_with_document,
    generate_practical_explanation
)
from config import Config

# Configure Streamlit page settings
st.set_page_config(
    page_title="PDF Summarizer & Quiz Generator",
    page_icon="📚",
    layout="wide"
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location and return the path."""
    try:
        # Validate file size
        if uploaded_file.size > Config.MAX_FILE_SIZE:
            st.error(f"File size exceeds maximum limit of {Config.MAX_FILE_SIZE / (1024 * 1024)}MB")
            return None
            
        # Validate file type
        if not uploaded_file.name.lower().endswith(tuple(Config.ALLOWED_FILE_TYPES)):
            st.error(f"Only {', '.join(Config.ALLOWED_FILE_TYPES)} files are allowed")
            return None
            
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

async def main():
    st.title("📚 Document Summarizer & Quiz Generator")
    st.write("Upload a PDF, PowerPoint, or Word document to generate a summary, quiz questions, and practical explanations!")

    # File upload section
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=Config.ALLOWED_FILE_TYPES,
        help="Supported formats: PDF (.pdf), PowerPoint (.ppt, .pptx), Word (.doc, .docx)"
    )
    text_chunks = None

    if uploaded_file is not None:
        with st.spinner("Processing document..."):
            file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                try:
                    # Process document content
                    text = extract_text_from_file(file_path)
                    text_chunks = split_text(text)
                    
                    # Create tabs for different features
                    tab1, tab2, tab3 = st.tabs(["📝 Summary", "❓ Quiz", "🔧 Practical Explanation"])
                    
                    # Summary tab
                    with tab1:
                        st.header("Document Summary")
                        if st.button("Generate Summary"):
                            with st.spinner("Generating summary..."):
                                summary = await generate_summary(text_chunks[0])
                                st.write(summary)
                                
                                st.download_button(
                                    label="Download Summary",
                                    data=summary,
                                    file_name="summary.txt",
                                    mime="text/plain"
                                )
                    
                    # Quiz tab
                    with tab2:
                        st.header("Quiz Generator")
                        col1, col2 = st.columns(2)
                        with col1:
                            num_questions = st.slider("Number of questions", min_value=3, max_value=10, value=5)
                        with col2:
                            quiz_difficulty = st.selectbox(
                                "Quiz Difficulty",
                                ["beginner", "intermediate", "advanced"],
                                index=1
                            )
                        
                        if st.button("Generate Quiz"):
                            with st.spinner("Generating quiz questions..."):
                                quiz = await generate_quiz(
                                    text_chunks[0],
                                    num_questions,
                                    quiz_difficulty
                                )
                                st.session_state.quiz = quiz
                                st.session_state.show_answers = [False] * len(quiz)
                        
                        if "quiz" in st.session_state:
                            # Display each question in a card-like format
                            for i, q in enumerate(st.session_state.quiz, 1):
                                st.markdown("---")  # Separator between questions
                                st.markdown(f"### Question {i}")
                                st.markdown(f"**{q['question']}**")
                                
                                # Display options
                                for option in q['options']:
                                    st.write(option)
                                
                                # Show answer and explanation
                                if st.button(f"Show Answer for Question {i}", key=f"answer_{i}"):
                                    st.session_state.show_answers[i-1] = not st.session_state.show_answers[i-1]
                                
                                if st.session_state.show_answers[i-1]:
                                    st.success(f"Correct Answer: {q['correct_answer']}")
                                    st.info(f"Explanation: {q['explanation']}")
                            
                            # Download button
                            formatted_quiz = format_quiz_for_display(st.session_state.quiz)
                            st.download_button(
                                label="Download Quiz",
                                data=formatted_quiz,
                                file_name="quiz.txt",
                                mime="text/plain"
                            )
                    
                    # Practical Explanation tab
                    with tab3:
                        st.header("Practical Explanation")
                        st.write("Get practical explanations and real-world examples of the document content")
                        
                        explanation_difficulty = st.selectbox(
                            "Explanation Difficulty",
                            ["beginner", "intermediate", "advanced"],
                            index=1
                        )
                        
                        if st.button("Generate Practical Explanation"):
                            with st.spinner("Generating practical explanation..."):
                                explanation = await generate_practical_explanation(
                                    text_chunks[0],
                                    explanation_difficulty
                                )
                                st.write(explanation)
                                
                                st.download_button(
                                    label="Download Explanation",
                                    data=explanation,
                                    file_name="practical_explanation.txt",
                                    mime="text/plain"
                                )
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    # Clean up temporary file
                    if os.path.exists(file_path):
                        os.remove(file_path)

    # Chat section - always visible
    st.markdown("---")
    st.header("💬 Chat with Document")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat difficulty selection
    chat_difficulty = st.selectbox(
        "Chat Difficulty",
        ["beginner", "intermediate", "advanced"],
        index=1
    )
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input and response
    if prompt := st.chat_input("Ask a question about the document"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if text_chunks is not None:
                    try:
                        response = await chat_with_document(
                            text_chunks[0],
                            prompt,
                            chat_difficulty
                        )
                    except Exception as e:
                        response = f"An error occurred: {str(e)}"
                else:
                    response = "Please upload a document first to ask questions about its content."
                st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    asyncio.run(main()) 