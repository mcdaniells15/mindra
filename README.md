# PDF Summarizer and Quiz Generator

This application uses Langchain and Google's Gemini API to analyze PDF documents, generate summaries, and create quizzes based on the content.

## Features

- PDF text extraction
- Document summarization
- Automatic quiz generation with multiple choice questions
- User-friendly web interface built with Streamlit
- Download options for both summaries and quizzes

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

To get a Google API key:
1. Go to the [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and paste it in your `.env` file

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Upload a PDF file using the file uploader

4. Use the tabs to:
   - Generate a summary of the document
   - Create quiz questions based on the content

5. Download the generated summary or quiz as text files

## Notes

- The application processes PDFs in chunks to handle large documents efficiently
- Quiz questions are generated using AI, so results may vary
- Make sure your PDF is text-based (not scanned images) for best results

## Dependencies

- langchain
- python-dotenv
- google-generativeai
- PyPDF2
- streamlit
- python-docx 