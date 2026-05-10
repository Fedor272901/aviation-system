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
# AIRPORTS
# =========================================================


class Airport(Base):
    __tablename__ = "AIRPORTS"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    code: Mapped[str] = mapped_column("CODE", String(3), unique=True)
    name: Mapped[str | None] = mapped_column("NAME", String(30))
    city: Mapped[str] = mapped_column("CITY", String(30))

    departing_flights: Mapped[list["Flight"]] = relationship(
        back_populates="from_airport", foreign_keys="Flight.id_from"
    )
    arriving_flights: Mapped[list["Flight"]] = relationship(
        back_populates="to_airport", foreign_keys="Flight.id_to"
    )

    def __repr__(self):
        return f"<Airport id={self.id} code={self.code}>"


# =========================================================
# AIRLINES
# =========================================================


class Airline(Base):
    __tablename__ = "AIRLINES"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("NAME", String(30), unique=True)
    code: Mapped[str] = mapped_column("CODE", String(3), unique=True)
    country: Mapped[str | None] = mapped_column("COUNTRY", String(30))

    flights: Mapped[list["Flight"]] = relationship(back_populates="airline")
    leases: Mapped[list["AircraftLease"]] = relationship(back_populates="airline")

    def __repr__(self):
        return f"<Airline id={self.id} code={self.code}>"

# =========================================================
# FLIGHT STATUS
# =========================================================


class FlightStatus(Base):
    __tablename__ = "FLIGHT_STATUSES"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    status_name: Mapped[str] = mapped_column("STATUS_NAME", String(20), unique=True)

    flights: Mapped[list["Flight"]] = relationship(back_populates="status")

    def __repr__(self):
        return f"<FlightStatus id={self.id} status_name={self.status_name}>"


# =========================================================
# FLIGHT
# =========================================================


class Flight(Base):
    __tablename__ = "FLIGHTS"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    flight_number: Mapped[str] = mapped_column("FLIGHT_NUMBER", String(10))
    departure_datetime: Mapped[datetime] = mapped_column(
        "DEPARTURE_DATETIME", DateTime(timezone=True)
    )
    arrival_datetime: Mapped[datetime] = mapped_column(
        "ARRIVAL_DATETIME", DateTime(timezone=True)
    )
    id_from: Mapped[int] = mapped_column("ID_FROM", ForeignKey("AIRPORTS.ID"))
    id_to: Mapped[int] = mapped_column("ID_TO", ForeignKey("AIRPORTS.ID"))
    id_airline: Mapped[int] = mapped_column("ID_AIRLINE", ForeignKey("AIRLINES.ID"))
    id_aircraft: Mapped[int] = mapped_column("ID_AIRCRAFT", ForeignKey("AIRCRAFT.ID"))
    id_status: Mapped[int] = mapped_column(
        "ID_STATUS", ForeignKey("FLIGHT_STATUSES.ID")
    )

    from_airport: Mapped["Airport"] = relationship(
        back_populates="departing_flights", foreign_keys=[id_from]
    )
    to_airport: Mapped["Airport"] = relationship(
        back_populates="arriving_flights", foreign_keys=[id_to]
    )
    airline: Mapped["Airline"] = relationship(back_populates="flights")
    aircraft: Mapped["Aircraft"] = relationship(back_populates="flights")
    status: Mapped["FlightStatus"] = relationship(back_populates="flights")

    prices: Mapped[list["FlightPrice"]] = relationship(back_populates="flight")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="flight")
    crew_assignments: Mapped[list["CrewAssignment"]] = relationship(
        back_populates="flight"
    )

    def __repr__(self):
        return f"<Flight id={self.id} number={self.flight_number}>"


# =========================================================
# FLIGHT PRICE
# =========================================================


class FlightPrice(Base):
    __tablename__ = "FLIGHT_PRICES"
    __table_args__ = (
        UniqueConstraint(
            "ID_FLIGHT", "ID_SEAT_CLASS", "VALID_FROM", name="UQ_FLIGHT_CLASS_DATE"
        ),
    )

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    id_flight: Mapped[int] = mapped_column("ID_FLIGHT", ForeignKey("FLIGHTS.ID"))
    id_seat_class: Mapped[int] = mapped_column(
        "ID_SEAT_CLASS", ForeignKey("SEAT_CLASSES.ID")
    )
    price: Mapped[Decimal] = mapped_column("PRICE", Numeric(10, 2))
    valid_from: Mapped[datetime] = mapped_column(
        "VALID_FROM",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        "VALID_TO", DateTime(timezone=True)
    )

    flight: Mapped["Flight"] = relationship(back_populates="prices")
    seat_class: Mapped["SeatClass"] = relationship(back_populates="flight_prices")

    def __repr__(self):
        return f"<FlightPrice id={self.id} flight={self.id_flight} seat_class={self.id_seat_class}>"
