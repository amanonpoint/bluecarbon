# helper/llm.py
import json
import re
from typing import Dict, Any
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")
        
        self.llm = ChatGroq(
            api_key=api_key,
            model=model,
            temperature=0.1,
        )

#     def generate_json_response(self, query: str, context: str) -> Dict[str, Any]:
#         """Smart JSON response with dynamic citation limits."""
#         prompt = f"""You are a statistics textbook assistant.

# USER QUERY: {query}

# BOOK CONTEXT:
# {context}

# Analyze the context and respond in STRICT JSON format only:

# {{
#   "answer": "Answer ONLY if directly found in context above. If not found: 'Not found in textbook.'",
#   "citation_required": "yes|no",
#   "citation_limit": 1|2|3,
#   "files_used": 1|2|3
# }}

# 📋 SMART CITATION RULES:
# 1. Answer ONLY if query is DIRECTLY in context
# 2. Count UNIQUE file_id's in context:
#    - 1 file → "files_used": 1, "citation_limit": 1
#    - 2 files → "files_used": 2, "citation_limit": 2  
#    - 3+ files → "files_used": 3, "citation_limit": 3
# 3. Same file multiple chunks → count as 1 file
# 4. citation_required: "yes" ONLY if answer uses context

# JSON ONLY - NO OTHER TEXT!"""

#         response = self.llm.invoke(prompt)
#         return self._parse_json_response(response.content)

#     def _parse_json_response(self, content: str) -> Dict[str, Any]:
#         """Robust JSON parser - extracts JSON even from messy LLM output."""
#         content = content.strip()
        
#         # Method 1: Find any JSON block
#         json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
#         if json_match:
#             try:
#                 return json.loads(json_match.group())
#             except json.JSONDecodeError:
#                 pass
        
#         # Method 2: Clean common LLM formatting junk
#         cleaned = re.sub(r'``````python|``````json|``````\n', '', content).strip()
#         cleaned = re.sub(r'^.*?(?=\{)', '', cleaned, flags=re.DOTALL)  # Remove text before {
#         cleaned = re.sub(r'(?<=\}).*?$', '', cleaned, flags=re.DOTALL)  # Remove text after }
        
#         json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)
#         if json_match:
#             try:
#                 return json.loads(json_match.group())
#             except json.JSONDecodeError:
#                 pass
        
#         # Method 3: Fallback - extract key values manually
#         answer_match = re.search(r'"answer"[:\s]*"([^"]*)"', content)
#         citation_match = re.search(r'"citation_required"[:\s]*"([^"]*)"', content)
        
#         fallback = {
#             "answer": answer_match.group(1) if answer_match else "Error parsing response.",
#             "citation_required": citation_match.group(1) if citation_match else "no",
#             "citation_limit": 0,
#             "files_used": 0
#         }
        
#         return fallback
    def session_name(self, query):
        prompt = f"""Based on the user query intent, generate the session name. 
    Output should be in strict JSON format with no additional text or markdown.

    #User Query: {query}

    #Output format:
    {{"session_name": "session name based on the user query intent", "user_query": "actual user query"}}
    """
        
        response = self.llm.invoke(prompt)
        
        # Parse the response
        try:
            # Handle different response types
            if hasattr(response, 'content'):
                text = response.content
            elif isinstance(response, str):
                text = response
            else:
                text = str(response)
            
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            
            # Strip whitespace
            text = text.strip()
            
            # Try to find JSON object in the text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)
            
            # Parse JSON
            parsed = json.loads(text)
            
            # Validate expected keys
            if 'session_name' not in parsed or 'user_query' not in parsed:
                raise ValueError("Response missing required keys: 'session_name' or 'user_query'")
            
            return parsed
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}. Response was: {text[:200]}")
        except Exception as e:
            raise ValueError(f"Error processing response: {e}")

    def generate_json_response(self, prompt):
            """Smart JSON response with dynamic citation limits."""
    #         prompt = f"""You are a statistics textbook assistant.

    # USER QUERY: {query}

    # BOOK CONTEXT:
    # {context}

    # Analyze the context and respond in STRICT JSON format only:

    # {{
    # "answer": "Answer ONLY if directly found in context above. If not found: 'Not found in textbook.'",
    # "citation_required": "yes|no",
    # "citation_limit": 1|2|3,
    # "files_used": 1|2|3
    # }}

    # 📋 SMART CITATION RULES:
    # 1. Answer ONLY if query is DIRECTLY in context
    # 2. Count UNIQUE file_id's in context:
    # - 1 file → "files_used": 1, "citation_limit": 1
    # - 2 files → "files_used": 2, "citation_limit": 2  
    # - 3+ files → "files_used": 3, "citation_limit": 3
    # 3. Same file multiple chunks → count as 1 file
    # 4. citation_required: "yes" ONLY if answer uses context

    # JSON ONLY - NO OTHER TEXT!"""

            response = self.llm.invoke(prompt)
            return self._parse_json_response(response.content)

    def _extract_json_block(self, text: str) -> str | None:
        """
        Extract the first valid JSON object using brace counting.
        Python-safe (no regex recursion).
        """
        start = text.find("{")
        if start == -1:
            return None

        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1

            if brace_count == 0:
                return text[start:i + 1]

        return None


    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        content = content.strip()

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())

                # Hard guarantees
                parsed.setdefault("used_chunk_ids", [])
                parsed.setdefault("chunk_reasoning", {})
                parsed.setdefault("citation_required", "no")
                parsed.setdefault("answer", "")

                # Enforce reasoning alignment
                if set(parsed["used_chunk_ids"]) != set(parsed["chunk_reasoning"].keys()):
                    raise ValueError("chunk_reasoning keys must match used_chunk_ids")

                return parsed

            except Exception:
                pass

        # Fallback (safe)
        return {
            "answer": "Error parsing response.",
            "citation_required": "no",
            "used_chunk_ids": [],
            "chunk_reasoning": {}
        }


    
    

    
        # """
        # Robust parser for LLM JSON responses.
        # Expected format:
        # {
        # "answer": "...",
        # "citation_required": "yes" | "no",
        # "used_chunk_ids": ["chk_xxx", "chk_yyy"]
        # }
        # """
        # content = content.strip()

        # # ---------------------------
        # # STEP 1: Extract JSON block
        # # ---------------------------
        # json_match = re.search(
        #     r'\{(?:[^{}]|(?R))*\}',
        #     content,
        #     re.DOTALL
        # )

        # if json_match:
        #     try:
        #         data = json.loads(json_match.group())
        #     except json.JSONDecodeError:
        #         data = {}
        # else:
        #     data = {}

        # # ---------------------------
        # # STEP 2: Normalize fields
        # # ---------------------------
        # answer = str(data.get("answer", "")).strip()
        # citation_required = str(data.get("citation_required", "no")).lower()

        # used_chunk_ids = data.get("used_chunk_ids", [])

        # # ---------------------------
        # # STEP 3: Validate chunk_ids
        # # ---------------------------
        # if not isinstance(used_chunk_ids, list):
        #     used_chunk_ids = []

        # # Keep only valid-looking chunk IDs
        # used_chunk_ids = [
        #     cid for cid in used_chunk_ids
        #     if isinstance(cid, str) and cid.startswith("chk_")
        # ]

        # # ---------------------------
        # # STEP 4: Auto-correct logic
        # # ---------------------------
        # if citation_required != "yes" or not used_chunk_ids:
        #     citation_required = "no"
        #     used_chunk_ids = []

        # # ---------------------------
        # # STEP 5: Safe fallback
        # # ---------------------------
        # if not answer:
        #     answer = "Not found in provided documents."

        # return {
        #     "answer": answer,
        #     "citation_required": citation_required,
        #     "used_chunk_ids": used_chunk_ids
        # }
