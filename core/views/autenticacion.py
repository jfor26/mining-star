"""
Inicio y cierre de sesion.

PROBLEMA ORIGINAL: la vista se llamaba "login" y solo hacia
render("login/index.html"). Nunca verificaba usuario ni contrasena, asi que
el formulario era decorativo: bastaba escribir /dashboard/ en la barra de
direcciones para entrar. Ademas el nombre "login" tapaba a la funcion
django.contrib.auth.login, que es justo la que hace falta aqui.
"""

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as iniciar_sesion_django
from django.contrib.auth import logout as cerrar_sesion_django
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST


@require_http_methods(["GET", "POST"])
def login_view(request):
    # Si ya inicio sesion, no tiene sentido mostrarle el formulario.
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        usuario = request.POST.get("usuario", "").strip()
        contrasena = request.POST.get("contrasena", "")

        # authenticate() compara contra el hash almacenado; nunca se
        # comparan contrasenas en texto plano.
        cuenta = authenticate(request, username=usuario, password=contrasena)

        if cuenta is not None:
            iniciar_sesion_django(request, cuenta)

            # Si el usuario venia de una pagina protegida, se le devuelve alli.
            destino = request.GET.get("next") or "dashboard"
            return redirect(destino)

        # Mensaje deliberadamente generico: decir "el usuario no existe"
        # le confirmaria a un atacante que usuarios son validos.
        messages.error(request, "Usuario o contrasena incorrectos.")

    return render(request, "login/index.html")


@require_POST
def logout_view(request):
    cerrar_sesion_django(request)
    messages.success(request, "Sesion cerrada correctamente.")
    return redirect("login")
