# app/schemas/server.py
import uuid
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs, urlunparse # Для работы с URL

from sqlmodel import SQLModel, Field
from pydantic import field_validator, ValidationInfo, AnyHttpUrl, HttpUrl

from app.models.enums import ServerType, LicenseType

# --- Константы ---
IIKO_UID_REGEX = re.compile(r"^\d{3}-\d{3}-\d{3}$")
# Список доменов облачных серверов (можно вынести в конфиг при желании)
CLOUD_DOMAINS = [".iiko.it", ".syrve.online"]
DEFAULT_LOCAL_PORT = 8080 # Порт по умолчанию, если не указан для локального RMS
RESTO_PATH = "/resto" # Стандартный путь

# --- Схемы ---

class ServerBase(SQLModel):
    name: str = Field(..., min_length=1, max_length=255)
    server_type: ServerType = Field(default=ServerType.RMS)
    point_id: uuid.UUID
    # iiko_uid валидируется ниже
    iiko_uid: str = Field(..., max_length=11)
    license_type: LicenseType = Field(default=LicenseType.CLOUD)
    # address и partner_portal_id будут нормализованы/провалидированы ниже
    address: Optional[str] = Field(default=None, max_length=512)
    connection_details: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None
    partner_portal_id: Optional[str] = Field(default=None, max_length=50) # Храним только ID

    # --- Валидаторы ---

    @field_validator('iiko_uid')
    @classmethod
    def validate_iiko_uid(cls, v: str) -> str:
        """4. Проверка формата iiko_uid."""
        if not IIKO_UID_REGEX.match(v):
            raise ValueError('Invalid iiko-UID format. Expected XXX-XXX-XXX')
        return v

    @field_validator('address', mode='before') # 'before' чтобы работать с сырым вводом
    @classmethod
    def normalize_and_validate_address(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """1. Нормализация и валидация адреса сервера."""
        if not v:
            # Если адрес не предоставлен, проверяем тип лицензии
            # Валидатор connection_details проверит обязательность подключения для Lifetime
            # Здесь просто возвращаем None, если адрес не указан
            return None

        address_str = str(v).strip().lower() # Приводим к нижнему регистру и убираем пробелы

        # Убираем /resto и другие пути в конце, если они есть
        for path_suffix in [RESTO_PATH, "/"]:
            if address_str.endswith(path_suffix):
                address_str = address_str[:-len(path_suffix)]

        # Проверяем на облачные домены
        is_cloud = False
        cloud_host = None
        for domain in CLOUD_DOMAINS:
            if domain in address_str:
                is_cloud = True
                # Пытаемся извлечь хост до облачного домена
                # Убираем схему, если есть
                if "://" in address_str:
                    address_str = address_str.split("://", 1)[1]
                # Находим позицию домена
                domain_pos = address_str.find(domain)
                if domain_pos != -1:
                    cloud_host = address_str[:domain_pos + len(domain)]
                    # Убираем возможный порт или путь после домена
                    if "/" in cloud_host:
                        cloud_host = cloud_host.split("/",1)[0]
                    if ":" in cloud_host:
                         # Проверяем, не является ли двоеточие частью IPv6 адреса
                         # Очень упрощенная проверка, лучше использовать urlparse
                         parsed_temp = urlparse(f"http://{cloud_host}") # Временно добавляем схему для парсинга
                         if parsed_temp.port: # Если парсер нашел порт, убираем его
                             cloud_host = parsed_temp.hostname

                break # Нашли первый облачный домен, выходим

        if is_cloud and cloud_host:
            # Формируем стандартный HTTPS URL для облака
            return f"https://{cloud_host}{RESTO_PATH}"
        else:
            # Считаем локальным RMS
            # Пытаемся разобрать как host[:port]
            parsed = urlparse(f"http://{address_str}") # Добавляем схему для парсинга
            host = parsed.hostname
            port = parsed.port

            if not host:
                 raise ValueError(f"Could not parse host from local address: {v}")

            # Если порт не был указан явно, используем дефолтный
            final_port = port if port else DEFAULT_LOCAL_PORT

            # Формируем стандартный HTTP URL для локального RMS
            return f"http://{host}:{final_port}{RESTO_PATH}"

    @field_validator('partner_portal_id', mode='before') # 'before' для работы с сырым вводом
    @classmethod
    def extract_and_validate_partner_id(cls, v: Optional[str]) -> Optional[str]:
        """2. Извлечение и валидация ID из ссылки или прямого ввода."""
        if not v:
            return None

        id_str = str(v).strip()

        # Пытаемся извлечь из URL
        if "://" in id_str and "clientId=" in id_str:
            try:
                parsed_url = urlparse(id_str)
                query_params = parse_qs(parsed_url.query)
                client_ids = query_params.get('clientId', [])
                if client_ids:
                    id_str = client_ids[0] # Берем первый clientId
                else:
                    raise ValueError(f"Could not find 'clientId' parameter in URL: {v}")
            except Exception as e:
                raise ValueError(f"Could not parse partner portal URL '{v}': {e}")

        # Проверяем, что результат состоит только из цифр
        if not id_str.isdigit():
            raise ValueError(f"Partner portal ID must contain only digits. Received: '{id_str}' from input '{v}'")

        # Ограничение длины (опционально, но полезно)
        if len(id_str) > 10: # Примерная длина
             raise ValueError(f"Partner portal ID seems too long: {id_str}")

        return id_str # Возвращаем только цифры ID

    # Валидатор для connection_details остается, он проверяет обязательность для Lifetime
    @field_validator('connection_details', mode='after')
    @classmethod
    def validate_connection_details(
        cls,
        v: Optional[Dict[str, Any] | List[Dict[str, Any]]],
        info: ValidationInfo
    ) -> Optional[Dict[str, Any] | List[Dict[str, Any]]]:
        license_type = info.data.get('license_type')
        server_name = info.data.get('name', '')
        address = info.data.get('address')

        # Проверяем обязательность подключения для Lifetime
        if license_type == LicenseType.LIFETIME and not v:
            # Добавляем адрес в сообщение об ошибке для ясности
            raise ValueError(f'Connection details required for Lifetime server "{server_name}" (Address: {address})')
        # Предупреждение для Cloud остается
        if license_type == LicenseType.CLOUD and v:
            print(f"Warning: Connection details provided for Cloud server '{server_name}' (Address: {address}). They might not be applicable.")
        return v

# --- Остальные схемы (Create, Read, Update) ---
# Они наследуют базовую схему и ее валидаторы

class ServerCreate(ServerBase):
    pass

class ServerRead(ServerBase):
    id: uuid.UUID
    revision: int
    point_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ServerUpdate(SQLModel):
    # Поля для обновления.
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    server_type: Optional[ServerType] = None
    license_type: Optional[LicenseType] = None
    address: Optional[str] = Field(default=None, max_length=512) # Будет нормализован валидатором
    connection_details: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None
    partner_portal_id: Optional[str] = Field(default=None, max_length=50) # Будет провалидирован/извлечен ID
    # iiko_uid: Optional[str] = Field(default=None, max_length=11) # Если разрешить обновление