# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router # Импортируем главный роутер v1

# Создаем экземпляр FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # Путь к схеме OpenAPI (Swagger)
)

# Настройка CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"], # Разрешаем все методы (GET, POST, PUT, DELETE и т.д.)
        allow_headers=["*"], # Разрешаем все заголовки
    )

# Подключаем роутер v1
app.include_router(api_router, prefix=settings.API_V1_STR)

# Просто корневой эндпоинт для проверки, что сервер работает
@app.get("/", tags=["Root"])
async def read_root():
    """
    Корневой эндпоинт для проверки доступности сервера.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Если нужно запускать напрямую через python app/main.py (для отладки)
# Но обычно используется uvicorn из командной строки
if __name__ == "__main__":
    import uvicorn
    # Запуск uvicorn сервера. reload=True автоматически перезапускает сервер при изменении кода.
    # В продакшене reload=True нужно убрать.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)