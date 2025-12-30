# helpers/session_manager.py
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.chat_models import ChatSessionDB, ChatMessageDB, ChatSession, ChatMessage
from database.postgres import get_async_session
import uuid
import json
from helper.llm import LLMClient

class SessionManager:
    def __init__(
            self,
            groq_model: str = "llama-3.3-70b-versatile",
    ):
        self.llm_client = LLMClient(groq_model)
    
    @staticmethod
    async def generate_session_name(first_query: str, groq_model: str = "llama-3.3-70b-versatile") -> str:
        """Generate session name from first query"""
        try:
            llm_client = LLMClient(groq_model)
            llm_response = llm_client.session_name(first_query)
            # llm_response is a dict with keys: 'session_name' and 'user_query'
            return llm_response.get('session_name')
        except Exception as e:
            # Fallback if LLM fails
            if len(first_query) > 50:
                return first_query[:47] + "..."
            return first_query
    
    @staticmethod
    async def create_session(
        user_id: Optional[str] = None,
        session_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> ChatSessionDB:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        if not session_name:
            session_name = f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        async with get_async_session() as db_session:
            new_session = ChatSessionDB(
                session_id=session_id,
                user_id=user_id,
                session_name=session_name,
                session_info=json.dumps(metadata or {}),  # ← Changed: use session_info
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(new_session)
            await db_session.commit()
            await db_session.refresh(new_session)
            return new_session
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[ChatSessionDB]:
        """Get session by ID"""
        async with get_async_session() as db_session:
            result = await db_session.execute(
                select(ChatSessionDB).where(ChatSessionDB.session_id == session_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_sessions(limit: int = 100, offset: int = 0) -> List[ChatSessionDB]:
        """Get all sessions with pagination"""
        async with get_async_session() as db_session:
            result = await db_session.execute(
                select(ChatSessionDB)
                .order_by(desc(ChatSessionDB.updated_at))
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        
    @staticmethod
    async def update_session(
        session_id: str, 
        session_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[ChatSessionDB]:
        """Update session"""
        async with get_async_session() as db_session:
            session = await SessionManager.get_session(session_id)
            if not session:
                return None
            
            if session_name:
                session.session_name = session_name
            if metadata:
                # Parse existing metadata
                existing_metadata = {}
                if session.session_info:
                    try:
                        existing_metadata = json.loads(session.session_info)
                    except:
                        pass
                
                # Merge and save
                merged_metadata = {**existing_metadata, **metadata}
                session.session_info = json.dumps(merged_metadata)  # ← Changed
            
            session.updated_at = datetime.utcnow()
            await db_session.commit()
            await db_session.refresh(session)
            return session
    
    @staticmethod
    async def delete_session(session_id: str) -> bool:
        """Delete session and all its messages"""
        async with get_async_session() as db_session:
            # Delete messages first
            await db_session.execute(
                delete(ChatMessageDB).where(ChatMessageDB.session_id == session_id)
            )
            
            # Delete session
            result = await db_session.execute(
                delete(ChatSessionDB).where(ChatSessionDB.session_id == session_id)
            )
            await db_session.commit()
            return result.rowcount > 0
    
    @staticmethod
    async def get_user_sessions(user_id: str) -> List[ChatSessionDB]:
        """Get all sessions for a user"""
        async with get_async_session() as db_session:
            result = await db_session.execute(
                select(ChatSessionDB)
                .where(ChatSessionDB.user_id == user_id)
                .order_by(ChatSessionDB.updated_at.desc())
            )
            return result.scalars().all()
    
    @staticmethod
    async def add_message(
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> ChatMessageDB:
        """Add message to session"""
        async with get_async_session() as db_session:
            message = ChatMessageDB(
                session_id=session_id,
                role=role,
                content=content,
                additional_data=json.dumps(metadata or {}),  # ← Changed: store as JSON string
                timestamp=datetime.utcnow()
            )
            db_session.add(message)
            
            # Update session timestamp
            await db_session.execute(
                update(ChatSessionDB)
                .where(ChatSessionDB.session_id == session_id)
                .values(updated_at=datetime.utcnow())
            )
            
            await db_session.commit()
            await db_session.refresh(message)
            return message
    
    @staticmethod
    async def get_session_messages(
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[ChatMessageDB]:
        """Get messages for a session"""
        async with get_async_session() as db_session:
            query = select(ChatMessageDB).where(
                ChatMessageDB.session_id == session_id
            ).order_by(ChatMessageDB.timestamp.asc())
            
            if limit:
                query = query.limit(limit)
            
            result = await db_session.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def get_session_with_messages(session_id: str) -> Optional[ChatSession]:
        """Get session with all messages - SIMPLE FIX"""
        session = await SessionManager.get_session(session_id)
        if not session:
            return None
        
        # Get messages
        messages = await SessionManager.get_session_messages(session_id)
        
        # Parse metadata safely
        session_metadata = {}
        if session.session_info:
            try:
                parsed = json.loads(session.session_info)
                if isinstance(parsed, dict):
                    session_metadata = parsed
            except:
                session_metadata = {}
        
        # Create messages with parsed metadata
        message_list = []
        for msg in messages:
            msg_metadata = {}
            if msg.additional_data:
                try:
                    parsed = json.loads(msg.additional_data)
                    if isinstance(parsed, dict):
                        msg_metadata = parsed
                except:
                    msg_metadata = {}
            
            message_list.append(
                ChatMessage(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    metadata=msg_metadata  # Already a dict
                )
            )
        
        return ChatSession(
            session_id=session.session_id,
            user_id=session.user_id,
            session_name=session.session_name,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session_metadata,  # Already a dict
            messages=message_list
        )