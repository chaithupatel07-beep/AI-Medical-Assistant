"""Authentication and User Profile Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import validate_password_strength


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return cleaned

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10, max_length=256)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def check_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def check_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    date_of_birth: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=130)
    gender: Optional[str] = Field(None, max_length=32)
    blood_type: Optional[str] = Field(None, max_length=16)
    allergies: Optional[str] = Field(None, max_length=2000)
    chronic_conditions: Optional[str] = Field(None, max_length=2000)
    emergency_contact: Optional[str] = Field(None, max_length=150)
    preferred_units: Optional[str] = Field(None, pattern="^(metric|imperial)$")


class UserProfileResponse(BaseModel):
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    preferred_units: str = "metric"
    updated_at: Optional[datetime] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    created_at: datetime
    profile: Optional[UserProfileResponse] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
