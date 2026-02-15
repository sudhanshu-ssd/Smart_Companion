# The Smart Companion: Neuro-Inclusive Executive Function Support 🧠✨

**The Smart Companion** is an advanced AI assistant built to bridge the "Executive Function Gap" for individuals with ADHD, Autism, and Dyslexia. Unlike generic assistants, it uses a custom state-machine architecture to deconstruct overwhelming goals into "Micro-Wins."

## 🚀 Key Innovation: The Smart Engine
The project features a custom-built execution pipeline:
* **Main Turn Function:** Orchestrates the flow between user input and system response.
* **Event Handler:** Manages asynchronous interactions and state updates.
* **Custom Scheduler:** Prioritizes tasks based on the user's "Energy Level" and their preferences/routines from their Neuro-Profile.
* **Executor & Render:** Processes task logic and renders a minimalist, single-task UI to prevent decision fatigue.

---

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python), SQLite
- **AI Engines:** Groq (llama-3.1-8b-instant ) & Google AI Studio (Gemini 2.5 Flash)
- **Frontend:** React + Vite, Tailwind CSS
- **Typography:** Lexend (Neuro-inclusive toggle)
- **Security:** Fernet (AES-128) Encryption-at-Rest , PII Masking

---

## 📦 Installation & Setup (Docker Compose)

### 1. Prerequisites
- Docker and Docker Compose installed.
- API keys for Groq and Google AI Studio.

### 2. Environment Variables
Create a `.env` file in the root directory like this:
API_KEY=your_groq_key_here
GEMINI_API_KEY=your_google_ai_studio_key_here

Repo provides a .env example too:

TO BUILD AND RUN THE DOCKER IMAGE,USE THESE COMMANDS in root directory(smart_companion):

docker-compose build
docker-compose up
