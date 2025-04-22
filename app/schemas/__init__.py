# app/schemas/__init__.py
from .token import Token, TokenPayload
from .company import CompanyBase, CompanyCreate, CompanyRead, CompanyUpdate
from .point import PointBase, PointCreate, PointRead, PointUpdate
from .server import ServerBase, ServerRead, ServerUpdate, ServerCreate
from .workstation import WorkstationBase, WorkstationCreate, WorkstationRead, WorkstationUpdate
from .fiscal_registrar import FiscalRegistrarBase, FiscalRegistrarCreate, FiscalRegistrarRead, FiscalRegistrarUpdate

# ... импорты для Server, Workstation, FiscalRegistrar ...

__all__ = [
    "Token", "TokenPayload",
    "CompanyBase", "CompanyCreate", "CompanyRead", "CompanyUpdate",
    "PointBase", "PointCreate", "PointRead", "PointUpdate",
    "ServerBase", "ServerCreate", "ServerRead", "ServerUpdate",
    "WorkstationBase", "WorkstationCreate", "WorkstationRead", "WorkstationUpdate",
    "FiscalRegistrarBase", "FiscalRegistrarBase", "FiscalRegistrarCreate", "FiscalRegistrarRead",
    # ...
]