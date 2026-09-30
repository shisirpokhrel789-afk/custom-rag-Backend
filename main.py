from fastapi import FastAPI

from database.connection import Base, engine
from models.booking import Booking
from models.document import DocumentChunk
from routes.chat import router as chat_router
from routes.documents import router as document_router


app = FastAPI(
    title="Custom Conversational RAG API",
    version="1.0.0",
)


Base.metadata.create_all(
    bind=engine
)


app.include_router(
    document_router
)

app.include_router(
    chat_router
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok"
    }
