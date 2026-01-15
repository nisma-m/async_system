from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    role: Optional[str] = "user"

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ProfileSchema(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Optional[Dict] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
