from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonBase(BaseModel):
    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)
    middle_name: str | None = Field(None, max_length=30)
    phone: str | None = Field(None, max_length=20)
    passport: str = Field(..., max_length=15)
    email: EmailStr


class PersonCreate(PersonBase):
    password: str = Field(..., min_length=6)


class PersonRead(PersonBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
