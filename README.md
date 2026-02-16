The Smart Companion: Neuro-Inclusive Executive Function Support 🧠✨
The Smart Companion is an adaptive AI companion built to bridge the "Executive Function Gap" for individuals with ADHD, Autism, and Dyslexia. Unlike generic assistants that add to the noise, this system uses a State-Machine Architecture to filter chaos into "Micro-Wins."

🚀 Key Innovations: The "Smart Companion" Engine
The backend features a custom execution pipeline designed for neurodivergent stability:

Bio-Rhythm Aware Planning: Automatically identifies the user's "Peak Focus Hours" and schedules high-difficulty tasks to match their energy cycles.

Micro-Step Decomposition: A specialized recursive prompt logic that ensures no task ever exceeds a 5-minute duration, preventing "task paralysis."

IST Time-Synchronicity: Optimized for local time zones (IST/UTC offset) to ensure routines and notifications hit at the exact right moment, regardless of server location.

Dopamine Reactor (Gamification): Integrated XP and Streak system with SQLite persistence to provide immediate rewards for task completion.

Stateful Memory: A session-based architecture that allows users to "Pause" and "Resume" tasks without losing context during interruptions.

🛠️ Tech Stack
Core: FastAPI (Python)

AI Orchestration: Groq (Llama 3.1 8B Instant) for high-speed logic & Gemini 1.5 Flash for visual context analysis.

Database: SQLite with Fernet (AES-128) Encryption-at-Rest for sensitive user data.

Frontend: React + Vite, Tailwind CSS, utilizing the Lexend typeface for maximum readability.

⚙️ Architecture Overview
Surgical PII Masker: Automatically scrubs emails, phone numbers, and IP addresses before they ever reach the LLM.

Intent Extractor: A high-precision classifier that distinguishes between casual conversation, deep planning, and routine updates.

The Scheduler: A decision-tree logic that manages UI states (Nudges, Celebrations, or Task Steps).

Database Worker: An asynchronous background checker that monitors the encrypted task queue for upcoming "Nudges."