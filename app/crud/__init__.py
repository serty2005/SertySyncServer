# app/crud/__init__.py
from .crud_company import company
from .crud_point import point
from .crud_server import server
from .crud_workstation import workstation
from .crud_fiscal_registrar import fiscal_registrar

__all__ = [
    "company",
    "point",
    "server",
    "workstation",
    "fiscal_registrar",
]