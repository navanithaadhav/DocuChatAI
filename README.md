# DocuChat AI - Full Stack RAG PDF Chatbot

DocuChat AI is a stunning, premium web application that allows users to upload PDF documents and converse with their contents using Retrieval-Augmented Generation (RAG).

## Features
- **Modern Glassmorphism Design:** Beautiful dark-mode UI with sleek animations, glowing text, and custom scrollbars.
- **RAG Pipeline:** Seamlessly extract PDF text, chunk documents, store fast local vector embeddings via ChromaDB, and leverage OpenAI for semantic answering.
- **Persistent AI Chat:** Real-time conversational memory out-of-the-box. Includes clear chat capability and source citations with precise page references.

---

## 🚀 Getting Started

### 1. Backend Setup (FastAPI & LangChain)
The backend uses Google Gemini AI (Google Generative AI).

1. Navigate to the backend directory:
   ```powershell
   cd backend
   ```
2. Create and activate a Virtual Environment (Recommended):
   ```powershell
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # If activation is blocked by Execution Policy:
   # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Install dependencies:
   ```powershell
   .\venv\Scripts\pip install -r requirements.txt
   ```
4. Set your API Key:
   Rename `.env.example` to `.env` and add your `GOOGLE_API_KEY` (or `GEMINI_API_KEY`).
5. Start the API server:
   ```powershell
   .\venv\Scripts\python -m uvicorn main:app --reload
   ```
   > The backend will map to `http://localhost:8000`.

### 2. Frontend Setup (React & Vite)
The frontend uses Tailwind CSS v3 for deep, vibrant colors and micro-interactions.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   > The frontend should generally map to `http://localhost:5173`.

---

## 🎨 Aesthetics & Architecture Highlights
- **Vibrant Gradients**: Deep dark mode combined with subtle violet/purple glowing background elements and `backdrop-blur-xl` panels for a highly premium feel.
- **Subtle Micro-Animations**: Buttons, upload areas, and AI status indicators feature responsive micro-interactions (`animate-pulse-slow`, `animate-slide-up`, etc.).
- **Smart RAG Design**: The RAG orchestrator supports memory tracking out of process bounds, and UI automatically cites direct sources inside the chatbot.
