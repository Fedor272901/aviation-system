from datetime import date
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Date,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Numeric,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# =========================================================
# SEAT CLASSES
# =========================================================


class SeatClass(Base):
    __tablename__ = "SEAT_CLASSES"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    class_name: Mapped[str] = mapped_column("CLASS_NAME", String(20), unique=True)
    price_multiplier: Mapped[Decimal] = mapped_column(
        "PRICE_MULTIPLIER", Numeric(3, 2), default=Decimal("1.00")
    )
    description: Mapped[str | None] = mapped_column("DESCRIPTION", String(100))

    model_seats: Mapped[list["ModelSeat"]] = relationship(back_populates="seat_class")
    flight_prices: Mapped[list["FlightPrice"]] = relationship(
        back_populates="seat_class"
    )
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="seat_class")

    def __repr__(self):
        return f"<SeatClass id={self.id} class_name={self.class_name}>"


# =========================================================
# MODEL AIRCRAFT
# =========================================================


class ModelAircraft(Base):
    __tablename__ = "MODEL_AIRCRAFT"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("NAME", String(30))
    manufacturer: Mapped[str | None] = mapped_column("MANUFACTURER", String(30))

    seats: Mapped[list["ModelSeat"]] = relationship(back_populates="model")
    aircraft: Mapped[list["Aircraft"]] = relationship(back_populates="model")

    def __repr__(self):
        return f"<ModelAircraft id={self.id} name={self.name}>"


# =========================================================
# MODEL SEATS
# =========================================================


class ModelSeat(Base):
    __tablename__ = "MODEL_SEATS"
    __table_args__ = (
        UniqueConstraint("ID_MODEL", "ID_SEAT_CLASS", name="UQ_MODEL_CLASS"),
        CheckConstraint("SEAT_COUNT > 0", name="CK_SEAT_COUNT"),
    )

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    id_model: Mapped[int] = mapped_column("ID_MODEL", ForeignKey("MODEL_AIRCRAFT.ID"))
    id_seat_class: Mapped[int] = mapped_column(
        "ID_SEAT_CLASS", ForeignKey("SEAT_CLASSES.ID")
    )
    seat_count: Mapped[int] = mapped_column("SEAT_COUNT", Integer)

    model: Mapped["ModelAircraft"] = relationship(back_populates="seats")
    seat_class: Mapped["SeatClass"] = relationship(back_populates="model_seats")

    def __repr__(self):
        return f"<ModelSeat id={self.id} model_id={self.id_model} class_id={self.id_seat_class}>"


# =========================================================
# AIRCRAFT
# =========================================================


class Aircraft(Base):
    __tablename__ = "AIRCRAFT"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    registration_number: Mapped[str] = mapped_column(
        "REGISTRATION_NUMBER", String(10), unique=True
    )
    id_model: Mapped[int] = mapped_column("ID_MODEL", ForeignKey("MODEL_AIRCRAFT.ID"))
    manufacture_year: Mapped[int | None] = mapped_column("MANUFACTURE_YEAR", Integer)
    last_maintenance: Mapped[date | None] = mapped_column("LAST_MAINTENANCE", Date)

    model: Mapped["ModelAircraft"] = relationship(back_populates="aircraft")
    flights: Mapped[list["Flight"]] = relationship(back_populates="aircraft")
    leases: Mapped[list["AircraftLease"]] = relationship(back_populates="aircraft")

    def __repr__(self):
        return f"<Aircraft id={self.id} reg={self.registration_number}>"


# =========================================================
# AIRCRAFT LEASE
# =========================================================


class AircraftLease(Base):
    __tablename__ = "AIRCRAFT_LEASE"
    __table_args__ = (
        CheckConstraint(
            "END_DATE IS NULL OR END_DATE > START_DATE", name="CK_LEASE_DATES"
        ),
    )

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    id_aircraft: Mapped[int] = mapped_column("ID_AIRCRAFT", ForeignKey("AIRCRAFT.ID"))
    id_airline: Mapped[int] = mapped_column("ID_AIRLINE", ForeignKey("AIRLINES.ID"))
    start_date: Mapped[date] = mapped_column("START_DATE", Date)
    end_date: Mapped[date | None] = mapped_column("END_DATE", Date)

    aircraft: Mapped["Aircraft"] = relationship(back_populates="leases")
    airline: Mapped["Airline"] = relationship(back_populates="leases")

    def __repr__(self):
        return f"<AircraftLease id={self.id} aircraft={self.id_aircraft} airline={self.id_airline}>"
