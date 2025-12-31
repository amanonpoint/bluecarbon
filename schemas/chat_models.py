# schemas/chat_models.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
import uuid

# Create declarative base
Base = declarative_base()

class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)
    session_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SIMPLEST: Don't use 'metadata' at all in SQLAlchemy model
    # Store metadata in a different column
    session_info = Column(Text, default='{}')  # Store JSON as text

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    message_id = Column(String, default=lambda: str(uuid.uuid4()))
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Store metadata as JSON text
    additional_data = Column(Text, default='{}')
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
# Pydantic Schemas
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('metadata', mode='before')
    @classmethod
    def convert_metadata(cls, v):
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        # If it's a MetaData or similar object
        if hasattr(v, '__dict__'):
            return v.__dict__
        # Try to convert to dict
        try:
            return dict(v)
        except:
            return {}

class ChatSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    session_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    messages: List[ChatMessage] = []
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    status: str
    query: str
    answer: str
    citation_required: bool
    # citation_limit: int
    # files_used: int
    citations: List[dict]
    chunks_retrieved: int
    session_id: str
    session_name: Optional[str] = None
    session_metadata: Optional[dict] = None
    memory_used: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)