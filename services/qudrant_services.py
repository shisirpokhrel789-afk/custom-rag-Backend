from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    ScoredPoint
)

from core.config import settings


class QdrantService:
    """
    Handles vector storage and similarity search using Qdrant.
    """

    VECTOR_SIZE = 384

    def __init__(self) -> None:

        self.client = QdrantClient(
            url=settings.qdrant_url
        )

        self.collection_name = (
            settings.qdrant_collection
        )

        self._create_collection()

    def _create_collection(self) -> None:

        collections = (
            self.client.get_collections()
        )

        existing_collections = {
            collection.name
            for collection in collections.collections
        }

        if self.collection_name not in existing_collections:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
    def delete_collection(self) -> None:
        self.client.delete_collection(
            collection_name=self.collection_name
        )

    def add_documents(
        self,
        embeddings: list[list[float]],
        chunks: list[str],
        document_id: int,
        filename: str,
    ) -> None:

        points: list[PointStruct] = []

        for index, (
            embedding,
            chunk,
        ) in enumerate(
            zip(embeddings, chunks)
        ):

            point = PointStruct(
                id=str(uuid4()),

                vector=embedding,

                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": index,
                    "content": chunk,
                },
            )

            points.append(point)

        if points:

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[ScoredPoint]:

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
        )

        return results.points
    
if __name__ == "__main__":
    client = QdrantClient(
        url=settings.qdrant_url
    )

    client.delete_collection(
        collection_name=settings.qdrant_collection
    )

    print("Qdrant collection deleted.")