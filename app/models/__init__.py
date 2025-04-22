from .base import BaseUUIDModel
from .enums import ServerType, LicenseType, ConnectionType # Добавить Enums
from .company import Company
from .point import Point
from .server import Server
from .workstation import Workstation
from .fiscal_registrar import FiscalRegistrar # Добавить FiscalRegistrar

# Можно добавить __all__ для явного экспорта
__all__ = [
    "BaseUUIDModel",
    "ServerType", "LicenseType", "ConnectionType",
    "Company",
    "Point",
    "Server",
    "Workstation",
    "FiscalRegistrar",
]