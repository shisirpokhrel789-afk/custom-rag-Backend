from sentence_transformers import SentenceTransformer

class EmbeddingsService:
    """
    Create Vector embeddings using Gorq model
    """
    def __init__(self):
       
        self.model=SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

   
    def create_embeddings(
            self,
            texts:list[str],

    )->list[list[float]]:

        if not texts:
            return []
        embedings=self.model.encode(
            texts,
            convert_to_numpy=True,
        )
        return embedings.tolist()
