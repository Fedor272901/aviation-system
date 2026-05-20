from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# =========================================================
# CREW
# =========================================================


class Crew(Base):
    __tablename__ = "CREW"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(
        "PERSON_ID", ForeignKey("PEOPLE.ID"), unique=True
    )

    person: Mapped["Person"] = relationship(back_populates="crew")
    assignments: Mapped[list["CrewAssignment"]] = relationship(back_populates="crew")

    def __repr__(self):
        return f"<Crew id={self.id} person_id={self.person_id}>"


# =========================================================
# FLIGHT ROLES
# =========================================================


class FlightRole(Base):
    __tablename__ = "FLIGHT_ROLES"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column("ROLE_NAME", String(20), unique=True)

    assignments: Mapped[list["CrewAssignment"]] = relationship(
        back_populates="flight_role"
    )

# =========================================================
# CREW ASSIGNMENTS
# =========================================================


class CrewAssignment(Base):
    __tablename__ = "CREW_ASSIGNMENTS"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    id_flight_role: Mapped[int] = mapped_column(
        "ID_FLIGHT_ROLE", ForeignKey("FLIGHT_ROLES.ID")
    )
    id_flight: Mapped[int] = mapped_column("ID_FLIGHT", ForeignKey("FLIGHTS.ID"))
    id_crew: Mapped[int] = mapped_column("ID_CREW", ForeignKey("CREW.ID"))

    flight_role: Mapped["FlightRole"] = relationship(back_populates="assignments")
    flight: Mapped["Flight"] = relationship(back_populates="crew_assignments")
    crew: Mapped["Crew"] = relationship(back_populates="assignments")

    def __repr__(self):
        return f"<CrewAssignment id={self.id} flight={self.id_flight} role={self.id_flight_role}>"
