"""Schemas de Auth."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr

from app.db.enums import UserRole


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CurrentUser(BaseModel):
    """Identidad inferida del JWT (no es la fila DB)."""

    id: uuid.UUID
    email: EmailStr
    role: UserRole
