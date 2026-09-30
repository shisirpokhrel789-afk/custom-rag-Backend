from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.chat import ChatRequest, ChatResponse
from services.rag import RAGService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:

    try:

        rag_service = RAGService(db)

        answer = rag_service.chat(
            session_id=request.session_id,
            user_message=request.message,
        )

        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {exc}",
        ) from exc