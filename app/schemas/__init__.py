# app/schemas/__init__.py
from .token import Token, TokenPayload # Оставляем схемы токена

# Импортируем схемы Company
from .company import CompanyBase, CompanyCreate, CompanyRead, CompanyUpdate

# ... здесь будут импорты схем для Point, Server и т.д. ...

# Можно определить __all__ для явного экспорта
__all__ = [
    "Token", "TokenPayload",
    "CompanyBase", "CompanyCreate", "CompanyRead", "CompanyUpdate",
    # ...
]