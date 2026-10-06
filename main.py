import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database
from agent import agent, reset_session

# Initialize DB
database.init_db()

app = FastAPI(
    title="AI Hostel Assistant API",
    description="Intelligent Conversational Agent and Management System for College Hostels",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    response: str
    action: str
    data: Optional[Any] = None
    session_id: str

class ComplaintCreateRequest(BaseModel):
    room_number: str
    description: str
    urgency: str
    category: Optional[str] = "General"
    student_name: Optional[str] = "Hostel Resident"

class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = ""

# API Endpoints
@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(payload: ChatRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    session_id = payload.session_id or "default_session"
    result = agent.process_message(payload.message, session_id=session_id)
    
    return ChatResponse(
        response=result["response"],
        action=result["action"],
        data=result.get("data"),
        session_id=session_id
    )

@app.post("/api/reset-session")
def reset_user_session(session_id: Optional[str] = "default_session"):
    reset_session(session_id)
    return {"status": "ok", "message": f"Session {session_id} reset successfully"}

@app.get("/api/complaints")
def list_complaints(room_number: Optional[str] = Query(None, description="Filter by room number")):
    return database.get_complaints(room_number=room_number)

@app.get("/api/complaints/{complaint_id}")
def get_complaint_details(complaint_id: str):
    complaint = database.get_complaint(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    return complaint

@app.post("/api/complaints")
def create_new_complaint(payload: ComplaintCreateRequest):
    if payload.urgency not in ["Low", "Medium", "High", "Urgent"]:
        raise HTTPException(status_code=400, detail="Invalid urgency level")
    complaint = database.create_complaint(
        room_number=payload.room_number,
        description=payload.description,
        urgency=payload.urgency,
        category=payload.category or "General",
        student_name=payload.student_name or "Hostel Resident"
    )
    return complaint

@app.patch("/api/complaints/{complaint_id}/status")
def update_status(complaint_id: str, payload: StatusUpdateRequest):
    if payload.status not in ["Registered", "In Progress", "Resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    updated = database.update_complaint_status(complaint_id, payload.status, payload.notes or "")
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return updated

@app.get("/api/mess-menu")
def get_menu(day: Optional[str] = None, meal: Optional[str] = None):
    return database.get_mess_menu(day_of_week=day, meal_type=meal)

@app.get("/api/rules")
def get_rules(category: Optional[str] = None, keyword: Optional[str] = None):
    return database.get_hostel_rules(category=category, keyword=keyword)

@app.get("/api/contacts")
def get_contacts(category: Optional[str] = None, query: Optional[str] = None):
    return database.get_staff_contacts(category=category, role_or_name=query)

# Mount static folder
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Hostel Assistant API is running. UI is located at /static/index.html"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
