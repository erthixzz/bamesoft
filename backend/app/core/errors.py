"""HTTP exceptions de dominio."""
from __future__ import annotations

from fastapi import HTTPException, status


class NotFound(HTTPException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, f"{resource} no encontrado")


class Forbidden(HTTPException):
    def __init__(self, msg: str = "No tienes permisos para esta acción") -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, msg)


class Unauthorized(HTTPException):
    def __init__(self, msg: str = "Credenciales inválidas") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, msg)


class Conflict(HTTPException):
    def __init__(self, msg: str = "El recurso ya existe") -> None:
        super().__init__(status.HTTP_409_CONFLICT, msg)


class BadRequest(HTTPException):
    def __init__(self, msg: str = "Solicitud inválida") -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, msg)
