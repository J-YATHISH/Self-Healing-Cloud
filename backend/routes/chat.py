from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import sys
import os
import base64
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.agent import chat_with_ai_async
except ImportError:
    chat_with_ai_async = None

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

@router.post("")
async def chat_endpoint(request: ChatRequest, authorization: str = Header(None)):
    """Chat with the Reliability Chatbot"""
    if chat_with_ai_async is None:
        raise HTTPException(status_code=503, detail="Chat service not available")
        
    user_id = "default_user"
    if authorization and authorization.startswith('Bearer '):
        try:
            token = authorization.replace('Bearer ', '')
            user_data = json.loads(base64.b64decode(token))
            user_id = user_data.get('user_id', 'default_user')
        except:
            pass
            
    try:
        result = await chat_with_ai_async(request.message, user_id=user_id)
        return result
    except Exception as e:
        print(f"❌ Chat Router Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
