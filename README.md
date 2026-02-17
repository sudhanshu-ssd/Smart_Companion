The Smart Companion: Neuro-Inclusive Executive Function Support 🧠✨
The Smart Companion is an adaptive AI companion built to bridge the "Executive Function Gap" for individuals with ADHD, Autism, and Dyslexia. Unlike generic assistants that add to the noise, this system uses a State-Machine Architecture to filter chaos into "Micro-Wins."
# The Smart Companion: Neuro-Inclusive Executive Function Support 🧠✨

**The Smart Companion** is an adaptive AI assistant built to bridge the "Executive Function Gap" for individuals with ADHD, Autism, and Dyslexia. It moves beyond simple "To-Do" lists by using a **State-Machine Architecture** to deconstruct overwhelming goals into manageable "Micro-Wins."

---

## 🚀 Key Innovations & Architecture

The system is built on a custom execution pipeline designed for stability and cognitive ease:

### 1. The Intent Extractor
High-precision classification that distinguishes between casual conversation, deep day-planning, micro-task decomposition, and routine management. It ensures the AI only triggers heavy planning when explicitly needed.

### 2. The Scheduler & Executor
* **Bio-Rhythm Awareness:** Automatically identifies user "Peak Focus Hours" from historical data and schedules high-difficulty tasks to match peak energy.
* **Recursive Decomposition:** Breaks any task into steps under 5 minutes.
* **State Management:** Supports `Pause`, `Resume`, and `Interruption` handling, allowing users to pivot between tasks without losing their place.

### 3. Time-Synchronicity (IST/UTC)
Optimized for local time zones (IST) regardless of server location (Render/Cloud). All database lookups and AI scheduling are synchronized with a +5:30 UTC offset to ensure routines trigger at the correct local time.

### 4. The Dopamine Reactor (Gamification)
Integrated XP, Leveling, and Streak systems. Task completion triggers a "Celebration" state, providing immediate neurochemical rewards for progress.

### 5. Privacy-First Security
* **Surgical PII Masking:** Automatically scrubs Emails, Phone Numbers, and IP addresses before sending data to LLMs.
* **Encryption-at-Rest:** User profiles and routines are stored in SQLite using **Fernet (AES-128)** symmetric encryption.

---

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **AI Models:** Groq (Llama 3.1 8B Instant) & Gemini 1.5 Flash
* **Database:** SQLite with Encryption-at-Rest
* **Frontend:** React + Vite, Tailwind CSS
* **Typography:** Lexend (Designed for readability and Dyslexia support)

---

## 📦 Docker Build & Run Instructions

This project is containerized for easy deployment across any environment.

### 1. Prerequisites
* Docker and Docker Compose installed.
* API keys for **Groq** and **Google AI Studio**.

### 2. Environment Variables
Create a `.env` file in the root directory like this:
API_KEY=your_groq_key_here
GEMINI_API_KEY=your_google_ai_studio_key_here

Repo provides a .env example too:

TO BUILD AND RUN THE DOCKER IMAGE,USE THESE COMMANDS in root directory(smart_companion):

docker-compose build


docker-compose up


DEMO LINK:-[https://smart-companion-coral.vercel.app](https://smart-companion-coral.vercel.app/)
"Backend is currently on a sleep-on-idle plan—initial request may take 30s to spin up. Subsequent actions will be near-instant."
