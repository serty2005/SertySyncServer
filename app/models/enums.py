# app/models/enums.py
import enum

class ServerType(str, enum.Enum):
    RMS = "RMS"
    CHAIN = "Chain"

class LicenseType(str, enum.Enum):
    LIFETIME = "Lifetime"
    CLOUD = "Cloud"

# Можно добавить и другие, например, типы подключений
class ConnectionType(str, enum.Enum):
    TEAMVIEWER = "Teamviewer"
    RDP = "RDP"
    ANYDESK = "Anydesk"
    LITEMANAGER = "Litemanager"
    OTHER = "Other"