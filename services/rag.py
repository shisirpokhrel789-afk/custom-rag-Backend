from datetime import date, datetime

from openai import OpenAI
from sqlalchemy.orm import Session

from core.config import settings
from schemas.booking import BookingData
from services.booking_extractor import BookingExtractor
from services.booking import BookingService
from services.embeddings import EmbeddingsService
from services.qudrant_services import QdrantService
from services.memory import RedisMemory


class RAGService:

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.chat_model = (
            settings.openai_chat_model
        )

        self.embedding_service = (
            EmbeddingsService()
        )

        self.qdrant = QdrantService()

        self.memory = RedisMemory()

        self.booking_extractor = (
            BookingExtractor()
        )

        self.booking_service = (
            BookingService(db)
        )

    def chat(
        self,
        session_id: str,
        user_message: str,
    ) -> str:

        # --------------------------------
        # 1. Load conversation history
        # --------------------------------

        history = self.memory.get_history(
            session_id
        )

        # --------------------------------
        # 2. Add current message temporarily
        # --------------------------------

        conversation = [
            *history,
            {
                "role": "user",
                "content": user_message,
            },
        ]

        # --------------------------------
        # 3. Ask LLM whether this is booking
        # --------------------------------

        booking_data = (
            self.booking_extractor.extract(
                conversation
            )
        )

        if booking_data.get("is_booking"):

            return self._handle_booking(
                session_id=session_id,
                user_message=user_message,
                booking_data=booking_data,
            )

        # --------------------------------
        # 4. Otherwise perform RAG
        # --------------------------------

        return self._handle_rag(
            session_id=session_id,
            user_message=user_message,
            history=history,
        )

    # ====================================
    # BOOKING
    # ====================================

    def _handle_booking(
        self,
        session_id: str,
        user_message: str,
        booking_data: dict,
    ) -> str:

        name = booking_data.get("name")
        email = booking_data.get("email")
        booking_date = booking_data.get("date")
        booking_time = booking_data.get("time")

        # Save current message first
        self.memory.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
        )

        # --------------------------------
        # Check missing fields
        # --------------------------------

        missing_fields: list[str] = []

        if not name:
            missing_fields.append("name")

        if not email:
            missing_fields.append("email")

        if not booking_date:
            missing_fields.append("date")

        if not booking_time:
            missing_fields.append("time")

        if missing_fields:

            response = (
                "Sure, I can help you book an interview. "
                "I still need: "
                + ", ".join(missing_fields)
                + "."
            )

            self.memory.add_message(
                session_id=session_id,
                role="assistant",
                content=response,
            )

            return response

        # --------------------------------
        # Validate booking data
        # --------------------------------

        try:

            validated_booking = BookingData(
                name=name,
                email=email,
                interview_date=booking_date,
                interview_time=booking_time,
            )

        except Exception:

            response = (
                "I couldn't validate the booking "
                "details. Please provide your name, "
                "email, date, and time in a valid format."
            )

            self.memory.add_message(
                session_id=session_id,
                role="assistant",
                content=response,
            )

            return response

        # --------------------------------
        # Store in MySQL
        # --------------------------------

        booking = (
            self.booking_service.create_booking(
                validated_booking
            )
        )

        response = (
            f"Your interview has been booked successfully. "
            f"Name: {booking.name}. "
            f"Email: {booking.email}. "
            f"Date: {booking.interview_date}. "
            f"Time: {booking.interview_time}."
        )

        self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=response,
        )

        return response

    # ====================================
    # RAG
    # ====================================

    def _handle_rag(
        self,
        session_id: str,
        user_message: str,
        history: list[dict[str, str]],
    ) -> str:

        # --------------------------------
        # 1. Create query embedding
        # --------------------------------

        query_embedding = (
            self.embedding_service.create_embeddings(
                [user_message]
            )[0]
        )

        # --------------------------------
        # 2. Search Qdrant
        # --------------------------------

        search_results = self.qdrant.search(
            query_embedding=query_embedding,
            top_k=5,
        )

        # --------------------------------
        # 3. Build context
        # --------------------------------

        context_parts: list[str] = []

        for result in search_results:

            payload = result.payload or {}

            content = payload.get(
                "content"
            )

            if content:
                context_parts.append(
                    str(content)
                )

        context = "\n\n---\n\n".join(
            context_parts
        )

        # --------------------------------
        # 4. Build prompt
        # --------------------------------

        system_prompt = """
You are a helpful conversational RAG assistant.

Answer using the provided document context.

Rules:

1. Use the uploaded document context
   whenever relevant.

2. Do not invent information.

3. If the answer is not available in
   the documents, say that you could not
   find the information in the uploaded
   documents.

4. Use previous conversation messages to
   understand follow-up questions.

5. Keep answers clear and concise.
"""

        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        # Previous conversation
        messages.extend(history)

        # Current question + retrieved context
        user_prompt = f"""
Relevant document context:

{context}

Current question:

{user_message}
"""

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        # --------------------------------
        # 5. Call LLM
        # --------------------------------

        response = self.client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=0.2,
        )

        answer = (
            response.choices[0]
            .message
            .content
            or "I could not generate an answer."
        )

        # --------------------------------
        # 6. Save conversation
        # --------------------------------

        self.memory.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
        )

        self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        return answer