from dataclasses import dataclass

@dataclass(frozen=True)
class TextChunk:
    index:int
    content:str
class TextChunker:
    def __init__(
        self,
        chunk_size:int=1000,
        chunk_overlap:int=200

    ):
        if chunk_overlap>=chunk_size:
            raise ValueError("Chunk_overlap must be smaller then cunk_size")
        self.chunk_size=chunk_size
        self.chunk_overlap=chunk_overlap

    def split(self,text:str)->list[TextChunk]:
        chunks:list[TextChunk]=[]
        start=0
        chunk_index=0

        while start<len(text):
            end=start+self.chunk_size
            chunk_text=text[start:end].strip()

            if chunk_text:
                chunks.append(
                    TextChunk(
                        index=chunk_index,
                        content=chunk_text,
                    )
                )

                chunk_index +=1
            start=end-self.chunk_overlap
        return chunks
    