# Self-Healing Cloud: AI-Driven SRE Mission Control

> [!NOTE]
> **Live Demo**: [Insert Deployed Link Here]

## 🌪️ The Problem
In modern cloud native environments, SREs (Site Reliability Engineers) are overwhelmed by "log noise." Identifying the root cause of an incident typically requires manually searching through thousands of multi-service traces, correlating disjointed logs, and guessing the remediation steps. This leads to high **MTTR (Mean Time To Recovery)** and system downtime.

## 🛡️ The Solution: Cloud RCA(Root Cause Analysis)
**Cloud RCA** is a Next-Gen SRE Command Center that transforms raw logs into actionable intelligence. By integrating **Gemini AI** directly into the GCP logging pipeline, it provides an autonomous diagnostic layer that identifies, explains, and suggests fixes for anomalies before they escalate.

---

## 🚀 Highlighted Features

- **Mission Control Dashboard**: A high-fidelity, real-time command center with dynamic System Health scores and AI Confidence metrics.
- **Reliability Chatbot**: A Gemini-powered assistant with context on the last 50+ incidents. Ask it deep questions about system behavior or remediation steps.
- **Neural Risk Distribution**: A scatter-plot visualization that correlates incident impact with AI confidence, enabling priority-based triage.
- **AI Deep Scan Engine**: Manually or automatically trigger parallel Gemini analyses across thousands of traces to find hidden anomalies.
- **Autonomy Control Layer**: Define and manage automation policies that trigger Slack/Email alerts or autonomous remediation when specific anomaly categories are detected.
- **Investigation Canvas**: A detailed view for every incident showing redacted trace summaries, correlation insights, and recommended actions.

---

## 💎 Why Cloud RCA? (USPs)

Unlike traditional logging tools (Datadog, Splunk, Cloud Logging) that focus on *storage* and *search*, Self-Healing Cloud focuses on **intent** and **resolution**.

-   **Trace-Centric Intelligence**: We don't just show logs; we group disparate logs from across your entire microservice stack into a single `trace_id` story. You see the *life* of a request, not just its death.
-   **Contextual Reasoning over Raw Data**: Most tools tell you *what* failed. Our Gemini-powered engine tells you *why* it failed and *how* to fix it, providing concrete remediation steps in seconds.
-   **Multi-Service Correlation**: Automatically detects when a failure in a database-service is the root cause of a timeout in the payment-service, linking them into a single Incident Group.
-   **Neural Prioritization**: High-volume errors are common. We use AI Confidence scores to separate "Background Noise" from "Critical Systemic Failures," so you focus on what actually matters.
-   **Zero-Index Zero-Config Persistence**: Built with custom in-memory filtering for Firestore, allowing the application to work out-of-the-box on any GCP project without the 24-hour wait for manual index creation.
-   **Evaluation Ready**: Features a **"Test Account with Real GCP Deployment"** mode, allowing stakeholders to witness the system's power on a live environment without OAuth onboarding friction.

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.9+
- Node.js (v18+)
- Google Cloud Project with Logging API enabled
- Gemini API Key (Google AI Studio)

### Backend Configuration
1. Navigate to the `backend/` folder.
2. Create a `.env` file from the following template:
   ```env
   GEMINI_API_KEY=your_gemini_key
   CREDENTIAL_ENCRYPTION_KEY=your_fernet_key
   GMAIL_USER=your_email
   GMAIL_APP_PASSWORD=your_app_password
   ```
3. Place your `serviceAccountKey.json` and `client_secret.json` in the `backend/` root.
4. Install dependencies: `pip install -r requirements.txt`.
5. Start the server: `python api.py`.

### Frontend Configuration
1. Navigate to the `frontend/` folder.
2. Install dependencies: `npm install`.
3. Start the dev server: `npm run dev`.
4. Open `http://localhost:5173`.

---

## 🏗️ Architecture
- **Frontend**: React, Vite, Tailwind CSS, Recharts, Framer Motion.
- **Backend**: FastAPI (Python), Asynchronous Firestore REST client.
- **Intelligence**: Gemini-3 Flash (Generative AI).
- **Communication**: Asynchronous Email (aiosmtplib).

---
