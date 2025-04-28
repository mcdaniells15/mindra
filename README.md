# Mindra


**Mindra** is an AI-powered tutoring platform that personalizes learning by breaking user queries into multi-level explanations (plain, mid, deep) and feeding the answer progressively using user metadata, tokenized analysis, and machine learning feedback. This project leverages xAI's Grok API (or a stubbed alternative), PDF extraction, Vue.js frontend, and a Dockerized PostgreSQL backend.

---

## ✨ Features
- Submit a question and receive tiered AI-generated explanations.
- Tokenization of AI responses into key terms, numbered steps, and sections.
- ML-based scoring of user answers for adaptive feedback.
- Generation of downloadable PDF summaries.
- Logs of API queries and session data.
- Docker-ready PostgreSQL integration.

---

## 🧵 Tech Stack

| Layer         | Technology             |
|---------------|-------------------------|
| Backend API   | Node.js + Express       |
| AI Integration| Grok API (or stub)      |
| Tokenizer     | JavaScript NLP utils    |
| ML Engine     | Python + PyTorch        |
| Frontend      | Vue 3 + Vite            |
| DB            | PostgreSQL (Docker)     |
| PDF Utility   | pdf-lib (Node.js)       |
| Dev Tools     | nodemon, dotenv, Docker |

---


---

## ✨ Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/jamesdonkoredu/Mindra.git
cd Mindra


chmod +x setup.sh
./setup.sh


cp .env.example .env
# Then open .env and update:
GROK_API_KEY=your-api-key
PORT=5050
DATABASE_URL=postgresql://mindra:devpass@localhost:5432/mindra

docker-compose up -d

#start backend
cd backend
npm install
npm run dev


#start frontend
cd frontend
npm install
npm run dev


#start ML model
cd backend/ml
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#Folder Structure
Mindra/
├── backend/                          # Node.js + Express backend
│   ├── api/
│   │   └── routes/
│   │       ├── query.js              # Handles POST /api/query
│   │       ├── results.js            # Handles POST /api/score
│   │       └── user.js               # Handles GET /api/user (stub)
│   ├── controllers/
│   │   ├── grokService.js            # Sends question to Grok API
│   │   └── scoringController.js      # ML scoring using token comparison
│   ├── database/
│   │   ├── models/
│   │   │   ├── Feedback.js           # Feedback entity for ML result
│   │   │   ├── Query.js              # Stores user-submitted queries
│   │   │   └── User.js               # Stores user metadata
│   │   └── init.sql                  # Optional DB setup file
│   ├── ml/
│   │   ├── model.py                  # PyTorch model definition
│   │   └── trainer.py                # Training logic (mocked)
│   ├── utils/
│   │   ├── pdfProcessor.js           # Converts Grok responses to PDF
│   │   ├── sectionParser.js          # Parses bold/numbered structure
│   │   └── tokenizer.js              # Tokenizes Grok output
│   ├── server.js                     # Entry point for Express app
│   ├── package.json                  # Backend dependencies + scripts
│   └── package-lock.json             # Backend lockfile
│
├── data/
│   ├── examples/
│   │   └── query_sessions.json       # Saved queries + Grok responses
│   └── logs/
│       └── api_logs.json             # Logs of API call timing/tokens
│
├── frontend/                         # Vue.js frontend app
│   ├── public/
│   │   └── index.html                # Entry HTML shell for SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── QueryInput.vue        # Component to submit user questions
│   │   │   └── ResultsViewer.vue     # Component to display results
│   │   ├── pages/
│   │   │   └── index.vue             # Landing page structure
│   │   ├── App.vue                   # App-level wrapper for router/view
│   │   └── main.js                   # Vue app initialization
│   ├── app.config.js                 # Frontend config for API URL etc.
│   ├── package.json                  # Frontend dependencies and dev scripts
│   └── package-lock.json             # Frontend lockfile
│
├── .env.example                      # Template for environment variables
├── docker-compose.yml               # Config to spin up PostgreSQL in Docker
├── setup.sh                         # Script to install backend, frontend, and DB
└── README.md                        # Full documentation of the Mindra project






#Example Query
#sample Postman send
{
  "question": "What is osmosis?"
}
#repsonse
{
  "question": "What is osmosis?",
  "responses": {
    "plain": "Water moves through membranes...",
    "mid": "Osmosis is the passive transport...",
    "deep": "At the molecular level, osmosis..."
  }
}


API Routes (Express)
POST /api/query → sends question to Grok or stub

POST /api/score → evaluates user answer with ML

Python ML Scripts
model.py → basic PyTorch scoring

trainer.py → mock training loop (future dev)

PDF Generation
pdfProcessor.js handles layout and section export

Data Logging
query_sessions.json stores each question + tiered answer

api_logs.json logs latency and key activity


#TO BE DONE

Add unit tests and Postman collection

Connect PDF download on frontend

Integrate real Grok API auth

Enable ML scoring feedback to user