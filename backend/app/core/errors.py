"""HTTP exceptions de dominio."""
from __future__ import annotations

from fastapi import HTTPException, status


class NotFound(HTTPException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, f"{resource} no encontrado")


class Forbidden(HTTPException):
    def __init__(self, msg: str = "No tienes permisos para esta acción") -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, msg)


# Marca que el frontend busca en el detalle del 403 para llevar al usuario a la
# pantalla de "acceso pendiente" en vez de mostrarle un error genérico.
NO_PROFILE_CODE = "SIN_PERFIL"


class NoProfile(Forbidden):
    """Se autenticó correctamente, pero nadie le ha dado acceso todavía.

    Ocurre sobre todo con inicio de sesión por Google: cualquiera puede
    autenticarse ante Google, pero solo un administrador de Bamesoft decide
    quién existe como usuario y en qué clínica.
    """

    def __init__(self) -> None:
        super().__init__(
            f"{NO_PROFILE_CODE}: tu cuenta aún no tiene acceso. "
            "Un administrador debe habilitarte en una clínica."
        )


class Unauthorized(HTTPException):
    def __init__(self, msg: str = "Credenciales inválidas") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, msg)


class Conflict(HTTPException):
    def __init__(self, msg: str = "El recurso ya existe") -> None:
        super().__init__(status.HTTP_409_CONFLICT, msg)


class BadRequest(HTTPException):
    def __init__(self, msg: str = "Solicitud inválida") -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, msg)
