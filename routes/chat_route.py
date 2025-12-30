# routes/chat.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid
from datetime import datetime
import json 

from schemas.chat_models import QueryRequest, QueryResponse, ChatSession
from helper.session_manager import SessionManager
from helper.core import RagOrchestrator
from utils.time_formatter import get_time_ago

router = APIRouter(prefix="/api/v1/chat", tags=["RAG Chat API"])

# Initialize RAG orchestrator
rag_orchestrator = RagOrchestrator()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Simple query processing with memory
    """
    try:
        # Get or create session
        if request.session_id:
            session = await SessionManager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            session_name = session.session_name
        else:
            # Create new session
            session_name = await SessionManager.generate_session_name(request.query)
            session = await SessionManager.create_session(
                user_id=request.user_id,
                session_name=session_name
            )
            request.session_id = session.session_id
        
        # Process query
        result = await rag_orchestrator.process_query(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        # Save to database
        await SessionManager.add_message(
            session_id=request.session_id,
            role="user",
            content=request.query
        )
        
        await SessionManager.add_message(
            session_id=request.session_id,
            role="assistant",
            content=result["answer"],
            metadata={
                "citation_required": result["citation_required"],
                "citation_limit": result["citation_limit"],
                "files_used": result["files_used"],
                "citations": result["citations"],
                "memory_used": result["memory_used"],
            }
        )
        
        return QueryResponse(
            status=result["status"],
            query=result["query"],
            answer=result["answer"],
            citation_required=result["citation_required"],
            citation_limit=result["citation_limit"],
            files_used=result["files_used"],
            citations=result["citations"],
            chunks_retrieved=result["chunks_retrieved"],
            session_id=request.session_id,
            session_name=session_name,
            memory_used=result["memory_used"],
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/{session_id}/clear")
async def clear_memory(session_id: str):
    """Clear memory for session"""
    try:
        from helper.memory import SimpleMemoryManager
        memory_manager = SimpleMemoryManager()
        await memory_manager.clear_session_memory(session_id)
        return {"message": "Memory cleared", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions", response_model=dict)
async def create_session(
    user_id: Optional[str] = None,
    session_name: Optional[str] = None,
    metadata: Optional[dict] = None
):
    """Create a new chat session"""
    try:
        session = await SessionManager.create_session(
            user_id=user_id,
            session_name=session_name,
            metadata=metadata
        )
        
        return {
            "session_id": session.session_id,
            "session_name": session.session_name,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/all", response_model=List[dict])
async def get_all_sessions(
    limit: int = Query(100, description="Number of sessions to return", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0)
):
    """Get all sessions (paginated)"""
    try:
        sessions = await SessionManager.get_all_sessions(limit=limit, offset=offset)
        
        result = []
        for session in sessions:
            # Get message count for each session
            messages = await SessionManager.get_session_messages(session.session_id)
            
            result.append({
                "session_id": session.session_id,
                "session_name": session.session_name,
                "user_id": session.user_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(messages),
                "last_chat_time_ago": get_time_ago(session.updated_at)
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/user/{user_id}", response_model=List[dict])
async def get_user_sessions(
    user_id: str,
    limit: int = Query(50, description="Number of sessions to return", ge=1, le=100),
    offset: int = Query(0, description="Offset for pagination", ge=0)
):
    """Get all sessions for a user"""
    try:
        sessions = await SessionManager.get_user_sessions(user_id, limit=limit, offset=offset)
        
        result = []
        for session in sessions:
            messages = await SessionManager.get_session_messages(session.session_id)
            
            result.append({
                "session_id": session.session_id,
                "session_name": session.session_name,
                "user_id": session.user_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(messages),
                "last_chat_time_ago": get_time_ago(session.updated_at)
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=dict)
async def get_session_details(session_id: str):
    """Get session details by ID"""
    try:
        session = await SessionManager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await SessionManager.get_session_messages(session_id)
        
        return {
            "session_id": session.session_id,
            "session_name": session.session_name,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(messages),
            "last_chat_time_ago": get_time_ago(session.updated_at)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/full", response_model=ChatSession)
async def get_session_with_messages(session_id: str):
    """Get a specific session with all messages"""
    try:
        session = await SessionManager.get_session_with_messages(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages"""
    try:
        success = await SessionManager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    session_name: Optional[str] = None,
    metadata: Optional[dict] = None
):
    """Update session details"""
    try:
        session = await SessionManager.update_session(
            session_id, 
            session_name, 
            metadata
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await SessionManager.get_session_messages(session_id)
        
        return {
            "session_id": session.session_id,
            "session_name": session.session_name,
            "updated_at": session.updated_at,
            "message_count": len(messages),
            "last_chat_time_ago": get_time_ago(session.updated_at)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = Query(100, description="Number of messages to return", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0)
):
    """Get messages for a session"""
    try:
        session = await SessionManager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await SessionManager.get_session_messages(session_id, limit=limit, offset=offset)
        
        result = []
        for msg in messages:
            metadata = json.loads(msg.additional_data) if msg.additional_data else {}
            result.append({
                "message_id": msg.message_id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "time_ago": get_time_ago(msg.timestamp),
                "metadata": metadata
            })
        
        return {
            "session_id": session_id,
            "session_name": session.session_name,
            "total_messages": len(await SessionManager.get_session_messages(session_id)),
            "messages": result,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))