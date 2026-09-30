from sqlalchemy.orm import Session

from models.document import DocumentChunk
from services.chunker import TextChunker
from services.document_parser import DocumentParser
from services.embeddings import EmbeddingsService
from services.qudrant_services import QdrantService


class IngestionService:

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

        self.parser = DocumentParser()

        self.chunker = TextChunker(
            chunk_size=1000,
            chunk_overlap=200,
        )

        self.embedding_service = (
            EmbeddingsService()
        )

        self.qdrant_service = QdrantService()

    def ingest(
        self,
        file_path: str,
        filename: str,
        file_type: str,
    ) -> int:

        # 1. Extract text
        text = self.parser.extract_text(
            file_path
        )

        if not text.strip():
            raise ValueError(
                "Document contains no extractable text."
            )

        # 2. Create chunks
        chunks = self.chunker.split(text)

        if not chunks:
            raise ValueError(
                "No chunks were created."
            )

        # 3. Create embeddings
        contents = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service
            .create_embeddings(contents)
        )

        # 4. Store metadata in MySQL
        document = DocumentChunk(
            document_name=filename,
            file_type=file_type,
            chunk_count=len(chunks),
        )

        self.db.add(document)

        # We need the ID before inserting Qdrant points
        self.db.flush()

        # 5. Store embeddings in Qdrant
        self.qdrant_service.add_documents(
            embeddings=embeddings,
            chunks=contents,
            document_id=document.id,
            filename=filename,
        )

        # 6. Commit MySQL transaction
        self.db.commit()

        return len(chunks)