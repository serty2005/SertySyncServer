# app/api/v1/api.py
from fastapi import APIRouter

# Сюда будем импортировать и подключать роутеры для конкретных ресурсов
from .endpoints import auth, companies

api_router = APIRouter()

# Пример подключения роутера (пока закомментирован, т.к. файла auth.py еще нет)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
# api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
# ... и так далее для других ресурсов