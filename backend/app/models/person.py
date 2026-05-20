from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base



# =========================================================
# PEOPLE
# =========================================================


class Person(Base):
    __tablename__ = "PEOPLE"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    last_name: Mapped[str] = mapped_column("LAST_NAME", String(30))
    first_name: Mapped[str] = mapped_column("FIRST_NAME", String(30))
    middle_name: Mapped[str | None] = mapped_column("MIDDLE_NAME", String(30))
    phone: Mapped[str | None] = mapped_column("PHONE", String(20))
    passport: Mapped[str] = mapped_column("PASSPORT", String(15), unique=True)
    email: Mapped[str] = mapped_column("EMAIL", String(100), unique=True)
    password_hash: Mapped[str] = mapped_column("PASSWORD_HASH", String(255))

    system_roles: Mapped[list["PeopleSystemRole"]] = relationship(
        back_populates="person"
    )
    crew: Mapped["Crew"] = relationship(back_populates="person", uselist=False)
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="passenger")

    def __repr__(self):
        return f"<Person id={self.id} email={self.email}>"


# =========================================================
# SYSTEM ROLES
# =========================================================


class SystemRole(Base):
    __tablename__ = "SYSTEM_ROLES"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column("ROLE_NAME", String(20), unique=True)

    people: Mapped[list["PeopleSystemRole"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"<SystemRole id={self.id} role_name={self.role_name}>"


class PeopleSystemRole(Base):
    __tablename__ = "PEOPLE_SYSTEM_ROLES"
    __table_args__ = (UniqueConstraint("PERSON_ID", "ROLE_ID", name="UQ_PERSON_ROLE"),)

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column("PERSON_ID", ForeignKey("PEOPLE.ID"))
    role_id: Mapped[int] = mapped_column("ROLE_ID", ForeignKey("SYSTEM_ROLES.ID"))

    person: Mapped["Person"] = relationship(back_populates="system_roles")
    role: Mapped["SystemRole"] = relationship(back_populates="people")
