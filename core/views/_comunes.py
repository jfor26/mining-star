"""Utilidades compartidas por las vistas."""

from django.http import JsonResponse


def es_ajax(request) -> bool:
    """True si la peticion viene por fetch/XMLHttpRequest desde el dashboard."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def respuesta_ok(mensaje: str) -> JsonResponse:
    return JsonResponse({"success": True, "message": mensaje})


def respuesta_error(errores) -> JsonResponse:
    return JsonResponse({"success": False, "errors": errores}, status=400)


def requiere_modulo(modulo, operacion=None):
    """Aplica la matriz de acceso por cargo (core/permisos.py) a las vistas web.

    Sin operacion explicita: GET se considera "ver" y POST "crear", que es
    como funcionan las pantallas de listado con formulario de alta.
    Si el cargo no tiene permiso responde 403 (PermissionDenied).
    """
    from functools import wraps

    from django.core.exceptions import PermissionDenied

    from ..permisos import CREAR, VER, puede

    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            op = operacion or (VER if request.method in ("GET", "HEAD") else CREAR)
            if not puede(request.user, modulo, op):
                raise PermissionDenied("Su cargo no tiene acceso a esta operacion.")
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador
