import streamlit as st
import os
from utils import (
    extract_text_from_pdf,
    split_text,
    generate_summary,
    generate_quiz,
    format_quiz_for_display,
    chat_with_document,
    generate_practical_explanation
)

# Configure Streamlit page settings
st.set_page_config(
    page_title="PDF Summarizer & Quiz Generator",
    page_icon="📚",
    layout="wide"
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location and return the path."""
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def main():
    st.title("📚 PDF Summarizer & Quiz Generator")
    st.write("Upload a PDF file to generate a summary, quiz questions, and practical explanations!")

    # File upload section
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    text_chunks = None

    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                # Process PDF content
                text = extract_text_from_pdf(file_path)
                text_chunks = split_text(text)
                
                # Create tabs for different features
                tab1, tab2, tab3 = st.tabs(["📝 Summary", "❓ Quiz", "🔧 Practical Explanation"])
                
                # Summary tab
                with tab1:
                    st.header("Document Summary")
                    if st.button("Generate Summary"):
                        with st.spinner("Generating summary..."):
                            summary = generate_summary(text_chunks[0])
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
                            quiz = generate_quiz(text_chunks[0], num_questions, quiz_difficulty)
                            formatted_quiz = format_quiz_for_display(quiz)
                            st.write(formatted_quiz)
                            
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
                            explanation = generate_practical_explanation(text_chunks[0], explanation_difficulty)
                            st.write(explanation)
                            
                            st.download_button(
                                label="Download Explanation",
                                data=explanation,
                                file_name="practical_explanation.txt",
                                mime="text/plain"
                            )
                
                # Clean up temporary file
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
                    response = chat_with_document(text_chunks[0], prompt, chat_difficulty)
                else:
                    response = "Please upload a document first to ask questions about its content."
                st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 