# app/crud/__init__.py

# Импортируем готовый к использованию объект 'company' из модуля crud_company
from .crud_company import company

# Когда вы создадите CRUD для других моделей, добавьте их сюда:
# from .crud_point import point
# from .crud_server import server
# from .crud_workstation import workstation
# from .crud_fiscal_registrar import fiscal_registrar

# (Опционально, но рекомендуется) Определяем __all__, чтобы указать,
# какие имена экспортируются при использовании 'from app.crud import *'
# Это также помогает инструментам статического анализа.
__all__ = [
    "company",
    # "point",
    # "server",
    # "workstation",
    # "fiscal_registrar",
]