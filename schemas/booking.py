from datetime import date, time

from pydantic import BaseModel, EmailStr, Field


class BookingData(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    email: EmailStr

    interview_date: date

    interview_time: time


class BookingResponse(BaseModel):
    id: int
    name: str
    email: str
    interview_date: date
    interview_time: time
    message: str