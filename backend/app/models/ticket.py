from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Numeric,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# =========================================================
# TICKET STATUS
# =========================================================


class TicketStatus(Base):
    __tablename__ = "TICKET_STATUSES"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    status_name: Mapped[str] = mapped_column("STATUS_NAME", String(20), unique=True)

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="status")

    def __repr__(self):
        return f"<TicketStatus id={self.id} status_name={self.status_name}>"


# =========================================================
# TICKET
# =========================================================


class Ticket(Base):
    __tablename__ = "TICKETS"
    __table_args__ = (
        UniqueConstraint("ID_FLIGHT", "SEAT_NUMBER", name="UQ_FLIGHT_SEAT"),
    )

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    seat_number: Mapped[str] = mapped_column("SEAT_NUMBER", String(5))
    id_seat_class: Mapped[int] = mapped_column(
        "ID_SEAT_CLASS", ForeignKey("SEAT_CLASSES.ID")
    )
    price: Mapped[Decimal] = mapped_column("PRICE", Numeric(10, 2))
    purchase_date: Mapped[datetime] = mapped_column(
        "PURCHASE_DATE",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    id_status: Mapped[int] = mapped_column(
        "ID_STATUS", ForeignKey("TICKET_STATUSES.ID")
    )
    id_flight: Mapped[int] = mapped_column("ID_FLIGHT", ForeignKey("FLIGHTS.ID"))
    id_passenger: Mapped[int] = mapped_column("ID_PASSENGER", ForeignKey("PEOPLE.ID"))

    seat_class: Mapped["SeatClass"] = relationship(back_populates="tickets")
    status: Mapped["TicketStatus"] = relationship(back_populates="tickets")
    flight: Mapped["Flight"] = relationship(back_populates="tickets")
    passenger: Mapped["Person"] = relationship(back_populates="tickets")

    def __repr__(self):
        return f"<Ticket id={self.id} flight={self.id_flight} seat={self.seat_number}>"
