# app/api/v1/api.py
from fastapi import APIRouter

# Импортируем все роутеры эндпоинтов
from .endpoints import auth, companies, points, servers, workstations, fiscal_registrars

api_router = APIRouter()

# Подключаем все роутеры
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(points.router, prefix="/points", tags=["Points"])
api_router.include_router(servers.router, prefix="/servers", tags=["Servers"])
api_router.include_router(workstations.router, prefix="/workstations", tags=["Workstations"])
api_router.include_router(fiscal_registrars.router, prefix="/fiscal-registrars", tags=["Fiscal Registrars"])