// =========================================================
// Pantalla de inicio de sesión
//
// IMPORTANTE: aquí ya no hay ninguna lógica de autenticación.
//
// La versión anterior de este archivo contenía:
//
//     if (usuario === "admin" && clave === "1234") { ... }
//
// es decir, el usuario y la contraseña estaban escritos en un archivo
// que el navegador descarga y que cualquiera puede leer con Ctrl+U.
// Además guardaba las cuentas en localStorage en texto plano y se
// limitaba a redirigir a /dashboard/, una página que no estaba
// protegida: escribir la URL a mano bastaba para entrar.
//
// Ahora las credenciales las verifica el servidor con
// django.contrib.auth.authenticate(), que compara contra un hash y
// nunca expone la contraseña. Este archivo solo tiene ayudas visuales.
// =========================================================

function mostrarClave() {

    const input = document.getElementById("clave");
    const icono = document.querySelector(".password-container i");

    if (!input || !icono) {
        return;
    }

    const oculta = input.type === "password";

    input.type = oculta ? "text" : "password";
    icono.classList.toggle("fa-eye", !oculta);
    icono.classList.toggle("fa-eye-slash", oculta);
}
