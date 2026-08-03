from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Esquema de Entrada (Input)
class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)

# Esquema de Saída (Output)
class UserResponse(BaseModel):
    id: int
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None)