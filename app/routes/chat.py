from fastapi import APIRouter
from app.models.schema import ChatRequest, ChatResponse
from app.services.rag import rag_pipeline

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = rag_pipeline(request.query)
    return ChatResponse(answer=result["answer"], contexts=result["contexts"])
