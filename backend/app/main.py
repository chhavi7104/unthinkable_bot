from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uuid
import asyncio

from .storage import create_session, save_message, get_conversation_history, update_session_status, get_session
from .llm_integration import LLMIntegration

app = FastAPI(title="AI Customer Support Bot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm_integration = LLMIntegration()

@app.post("/sessions/")
async def create_session_endpoint():
    session_id = str(uuid.uuid4())
    await create_session(session_id)
    return {"session_id": session_id, "status": "active"}

@app.post("/sessions/{session_id}/message")
async def send_message(session_id: str, message: Dict[str, Any]):
    # Verify session exists
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    user_message = message.get("message", "")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Get conversation history
    conversation_history = await get_conversation_history(session_id)
    
    # Save user message
    await save_message(session_id, user_message, is_user=True)
    
    # Generate AI response
    ai_response = llm_integration.generate_response(
        session_id, user_message, conversation_history
    )
    
    # Save AI response
    await save_message(
        session_id, 
        ai_response["response"], 
        is_user=False, 
        requires_escalation=ai_response["requires_escalation"]
    )
    
    # Update session status if escalation needed
    if ai_response["requires_escalation"]:
        await update_session_status(session_id, "escalated")
        session["status"] = "escalated"
    
    return {
        "response": ai_response["response"],
        "requires_escalation": ai_response["requires_escalation"],
        "next_action": ai_response["next_action"],
        "session_status": session["status"]
    }

@app.get("/sessions/{session_id}/history")
async def get_conversation_history_endpoint(session_id: str):
    messages = await get_conversation_history(session_id)
    return messages

@app.post("/sessions/{session_id}/escalate")
async def escalate_conversation(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get conversation history for summary
    messages = await get_conversation_history(session_id)
    
    conversation_history = [
        {
            "message": msg["message"],
            "is_user": msg["is_user"]
        }
        for msg in messages
    ]
    
    summary = llm_integration.summarize_conversation(conversation_history)
    
    await update_session_status(session_id, "escalated")
    
    return {
        "status": "escalated",
        "summary": summary,
        "message": "Conversation escalated to human agent"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": str(asyncio.get_event_loop().time())}

@app.get("/")
async def root():
    return {"message": "AI Customer Support Bot API"}