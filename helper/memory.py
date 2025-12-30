# helper/memory.py
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid
from collections import defaultdict

class SimpleMemoryManager:
    """Pure Python memory manager - no external dependencies"""
    
    def __init__(self, max_memories_per_session: int = 20):
        self.max_memories = max_memories_per_session
        self._session_memories = {}  # {session_id: list of memories}
        self._session_summaries = {}  # {session_id: summary}
        
    async def add_to_memory(
        self, 
        session_id: str, 
        user_message: str, 
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add conversation to session memory"""
        if session_id not in self._session_memories:
            self._session_memories[session_id] = []
            self._session_summaries[session_id] = ""
        
        # Create memory entry
        memory_entry = {
            'id': str(uuid.uuid4()),
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Add to memories
        self._session_memories[session_id].append(memory_entry)
        
        # Keep only last N memories
        if len(self._session_memories[session_id]) > self.max_memories:
            self._session_memories[session_id] = self._session_memories[session_id][-self.max_memories:]
        
        # Update summary every 5 messages
        if len(self._session_memories[session_id]) % 5 == 0:
            await self._update_summary(session_id)
    
    async def get_memory_context(self, session_id: str, query: str, limit: int = 5) -> str:
        """Get relevant memory context for query"""
        if session_id not in self._session_memories:
            return ""
        
        memories = self._session_memories[session_id]
        if not memories:
            return ""
        
        # Build context parts
        context_parts = []
        
        # Add summary if available
        summary = self._session_summaries.get(session_id)
        if summary:
            context_parts.append(f"## CONVERSATION SUMMARY\n{summary}")
        
        # Add relevant memories based on keyword matching
        relevant = self._find_relevant_memories(memories, query, limit)
        if relevant:
            relevant_text = []
            for memory in relevant:
                relevant_text.append(f"User: {memory['user_message']}")
                relevant_text.append(f"Assistant: {memory['ai_response'][:200]}...")
            
            context_parts.append(f"## RELEVANT PREVIOUS DISCUSSION\n" + "\n".join(relevant_text))
        
        # Add recent memories (if we don't have enough relevant ones)
        if len(relevant) < 3 and len(memories) > 0:
            recent = memories[-3:]  # Last 3 exchanges
            recent_text = []
            for memory in recent:
                recent_text.append(f"User: {memory['user_message']}")
                recent_text.append(f"Assistant: {memory['ai_response'][:150]}...")
            
            context_parts.append(f"## RECENT CONVERSATION\n" + "\n".join(recent_text))
        
        if context_parts:
            return "\n\n".join(context_parts) + "\n\n"
        return ""
    
    def _find_relevant_memories(self, memories: List[Dict], query: str, limit: int = 5) -> List[Dict]:
        """Find memories relevant to query using simple keyword matching"""
        if not memories or not query:
            return []
        
        query_words = set(query.lower().split())
        relevant = []
        
        for memory in reversed(memories):  # Most recent first
            # Check both user message and AI response
            combined_text = f"{memory['user_message']} {memory['ai_response']}".lower()
            
            # Count overlapping words
            memory_words = set(combined_text.split())
            overlap = len(query_words.intersection(memory_words))
            
            if overlap > 0:
                relevant.append((memory, overlap))
                if len(relevant) >= limit:
                    break
        
        # Sort by relevance
        relevant.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in relevant]
    
    async def _update_summary(self, session_id: str):
        """Create/update summary for session (simplified)"""
        if session_id not in self._session_memories:
            return
        
        memories = self._session_memories[session_id]
        if len(memories) < 3:
            return
        
        # Simple summary: extract main topics from last few conversations
        recent_topics = []
        for memory in memories[-5:]:
            user_msg = memory['user_message'][:100]
            recent_topics.append(f"- User asked about: {user_msg}...")
        
        if recent_topics:
            self._session_summaries[session_id] = "Recent topics:\n" + "\n".join(recent_topics)
    
    async def clear_session_memory(self, session_id: str):
        """Clear memory for a session"""
        if session_id in self._session_memories:
            del self._session_memories[session_id]
        if session_id in self._session_summaries:
            del self._session_summaries[session_id]
        print(f"✓ Cleared memory for session: {session_id}")
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about session memory"""
        memory_count = len(self._session_memories.get(session_id, []))
        has_summary = bool(self._session_summaries.get(session_id, ""))
        
        return {
            'session_id': session_id,
            'has_memory': memory_count > 0,
            'memory_count': memory_count,
            'has_summary': has_summary,
            'provider': 'simple_memory_manager'
        }