import json
import aiofiles
import os
from datetime import datetime
from typing import Dict, List, Any

STORAGE_FILE = "conversations.json"

async def load_conversations() -> Dict[str, Any]:
    """Load conversations from JSON file"""
    try:
        async with aiofiles.open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        return {"sessions": {}, "messages": {}}
    except json.JSONDecodeError:
        return {"sessions": {}, "messages": {}}

async def save_conversations(data: Dict[str, Any]):
    """Save conversations to JSON file"""
    async with aiofiles.open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, indent=2, default=str))

async def create_session(session_id: str):
    """Create a new session"""
    data = await load_conversations()
    data["sessions"][session_id] = {
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    if session_id not in data["messages"]:
        data["messages"][session_id] = []
    await save_conversations(data)

async def save_message(session_id: str, message: str, is_user: bool, requires_escalation: bool = False):
    """Save a message"""
    data = await load_conversations()
    
    # Ensure session exists
    if session_id not in data["sessions"]:
        await create_session(session_id)
    
    # Ensure messages list exists for this session
    if session_id not in data["messages"]:
        data["messages"][session_id] = []
    
    data["messages"][session_id].append({
        "message": message,
        "is_user": is_user,
        "timestamp": datetime.now().isoformat(),
        "requires_escalation": requires_escalation
    })
    await save_conversations(data)

async def get_conversation_history(session_id: str) -> List[Dict[str, Any]]:
    """Get conversation history"""
    data = await load_conversations()
    return data["messages"].get(session_id, [])

async def update_session_status(session_id: str, status: str):
    """Update session status"""
    data = await load_conversations()
    if session_id in data["sessions"]:
        data["sessions"][session_id]["status"] = status
        data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
        await save_conversations(data)

async def get_session(session_id: str) -> Dict[str, Any]:
    """Get session info"""
    data = await load_conversations()
    return data["sessions"].get(session_id)