from datetime import datetime
from sqlalchemy import DateTime,Integer,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column

from database.connection import Base

class DocumentChunk(Base):
    __tablename__="document_chunks"
    id:Mapped[int]=mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    document_name:Mapped[str]=mapped_column(
        String(255),
        nullable=False,
    )
    
    chunk_count:Mapped[int]=mapped_column(
        Integer,
        nullable=False
    )

    file_type:Mapped[str]=mapped_column(
        String(20),
        nullable=False
    )
    crated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

