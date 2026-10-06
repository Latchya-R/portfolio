# 🏢 HostelMate AI — College Hostel Assistant

An intelligent, full-stack AI-powered conversational assistant designed for university hostels. Students can ask questions regarding hostel amenities, mess timings, 7-day food menus, curfews, guidelines, and staff contacts, as well as lodge and track maintenance tickets in real-time.

---

## 🌟 Key Features

1. **Hostel Database Q&A (SQLite)**
   - Answers questions strictly using the pre-seeded SQLite database (`hostel.db`).
   - "What time is dinner?"
   - "What is today's mess menu?"
   - "What are the hostel rules?"
   - "Who should I contact for maintenance?"

2. **Smart Maintenance Action & Slot-Filling**
   - **Direct Lodging:** If room number is provided upfront (*"The fan in room 205 is not working."*), registers the ticket immediately.
   - **Multi-turn Dialogue:** If room number is missing (*"There is water leakage in my bathroom."*), the assistant detects the complaint and prompts the student for their room number before finalizing.
   - **Unique ID Generation:** Creates tracked tickets like `CMP-4892` with initial status set to **`Registered`**.

3. **Automated Urgency Classification**
   - **Urgent:** Fire, smoke, electrical sparks, short circuits (*"There is smoke coming from an electrical board"*).
   - **High:** Water leaks, ceiling leaks, pipe bursts, bathroom flooding (*"Water is leaking from the ceiling"*).
   - **Medium:** Broken fans, room lights, sockets, AC issues (*"My room light is not working"*, *"The fan in room 205 is not working"*).
   - **Low:** Minor squeaky doors, loose hinges, dustbin replacement requests, paint chips.

4. **Modern Chat Interface**
   - Built with Tailwind CSS and Lucide icons.
   - Real-time chat bubbles with Markdown rendering.
   - Interactive Complaint Confirmation Cards with color-coded urgency badges.
   - Slide-over **Complaints Tracker** drawer with room filtering.
   - Interactive **Weekly Mess Schedule** modal.
   - One-click suggestion chips for instant testing.

---

## 🚀 Quick Start

### 1. Requirements
Ensure Python 3.10+ is installed. Dependencies are listed in `requirements.txt`:
```bash
py -m pip install -r requirements.txt
```

### 2. Start the Server
Run with Python:
```bash
py main.py
```
Or directly using Uvicorn:
```bash
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open the Web Application
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Running Automated Tests

Run the unit tests (agent intent parsing, slot-filling, urgency rules):
```bash
py test_agent.py
```

Run the backend API integration tests:
```bash
py test_api.py
```

---

## 📁 Project Structure

```
├── main.py              # FastAPI server & API routes
├── agent.py             # Dialogue manager, urgency classifier, slot-filling
├── database.py          # SQLite schema, queries, and initial data seeding
├── requirements.txt     # Python dependencies (FastAPI, Uvicorn, Pydantic)
├── test_agent.py        # Unit tests for conversational AI and classifications
├── test_api.py          # Integration tests for REST endpoints
├── static/
│   ├── index.html       # Modern responsive web chat interface
│   ├── style.css        # Custom styles and urgency badge animations
│   └── app.js           # Client-side chat logic & API interaction
└── hostel.db            # SQLite database file (auto-generated)
```
