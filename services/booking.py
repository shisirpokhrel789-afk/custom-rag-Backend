from sqlalchemy.orm import Session

from models.booking import Booking
from schemas.booking import BookingData


class BookingService:

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

    def create_booking(
        self,
        booking_data: BookingData,
    ) -> Booking:

        booking = Booking(
            name=booking_data.name,
            email=str(booking_data.email),
            interview_date=booking_data.interview_date,
            interview_time=booking_data.interview_time,
        )

        self.db.add(booking)

        self.db.commit()

        self.db.refresh(booking)

        return booking