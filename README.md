# LinkedIn Auto Comment Generator

Automatically scrape LinkedIn posts and generate AI-powered comments using Playwright or Selenium — with a simple web UI to control everything.

---

## How It Works

1. You log in to LinkedIn once — the session is saved
2. Pick a scraper (Playwright or Selenium) from the UI
3. The app scrapes your feed, generates comments using Groq AI, and displays them

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Google Chrome installed
- A free [Groq API key](https://console.groq.com/keys)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/paragliderr/Linkedin-auto-comment
cd Linkedin-auto-comment
```

### 2. Create virtual environment and install dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
cd ..

pip install -r requirements.txt
pip install playwright
playwright install
```

### 3. Set up environment variables

**Root `.env`** (for Selenium chatbot):
```bash
cp .env.example .env
```
Fill in:
```properties
CHATBOT_URL=https://api.groq.com/openai/v1/chat/completions
CHATBOT_API=your-groq-api-key
CHATBOT_MODEL=llama-3.3-70b-versatile
```

**`Ai_services/.env`** (for Playwright/backend chatbot):
```bash
cp Ai_services/.env.example Ai_services/.env
```
Fill in:
```properties
CHATBOT_API_KEY=your-groq-api-key
BASE_URL=https://api.groq.com/openai/v1
MODEL_NAME=llama-3.3-70b-versatile
```

> Both can use the same Groq API key.

### 4. Log in to LinkedIn

Run this once — it opens a browser, you log in manually, and your session is saved for both scrapers:

```bash
source backend/.venv/bin/activate
python3 -m auto_sel.auth.unified_login
```

---

## Running the App

You need two terminals.

**Terminal 1 — Backend:**
```bash
source backend/.venv/bin/activate
python3 -m uvicorn backend.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Re-login

If your LinkedIn session expires, just run the login script again:

```bash
python3 -m auto_sel.auth.unified_login
```

---

## Models

The app uses [Groq](https://console.groq.com) for fast, free AI inference. Recommended model: `llama-3.3-70b-versatile`

Check [Groq's model list](https://console.groq.com/docs/models) if you need to switch models in the future.

---

## Project Structure

```
Linkedin-auto-comment/
├── auto_sel/          # Selenium scraper + auth
├── automation/        # Playwright scraper
├── Ai_services/       # AI chatbot for Playwright path
├── backend/           # FastAPI backend
├── frontend/          # Vue.js frontend
├── unified_pipeline.py
└── .env               # Your credentials (never commit this)
```
