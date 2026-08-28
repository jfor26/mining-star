"""Utilidades compartidas por las vistas."""

from django.http import JsonResponse


def es_ajax(request) -> bool:
    """True si la peticion viene por fetch/XMLHttpRequest desde el dashboard."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def respuesta_ok(mensaje: str) -> JsonResponse:
    return JsonResponse({"success": True, "message": mensaje})


def respuesta_error(errores) -> JsonResponse:
    return JsonResponse({"success": False, "errors": errores}, status=400)
