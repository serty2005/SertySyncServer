# app/schemas/token.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None # Subject (обычно username или user id)
    exp: Optional[datetime] = None # Expiry timestamp