// =========================================
// MOSTRAR / OCULTAR CONTRASEÑA
// =========================================

function mostrarClave() {

    const input = document.getElementById("clave");

    const icono = document.querySelector(
        ".password-container i"
    );

    if (input.type === "password") {

        input.type = "text";

        icono.classList.remove(
            "fa-eye"
        );

        icono.classList.add(
            "fa-eye-slash"
        );

    } else {

        input.type = "password";

        icono.classList.remove(
            "fa-eye-slash"
        );

        icono.classList.add(
            "fa-eye"
        );

    }

}


// =========================================
// NOTIFICACIÓN
// =========================================

function mostrarNotificacion(
    mensaje,
    tipo
) {

    alert(mensaje);

}


// =========================================
// INICIAR SESIÓN
// =========================================

function iniciarSesion() {

    const usuario =
        document.getElementById(
            "usuario"
        ).value.trim();

    const clave =
        document.getElementById(
            "clave"
        ).value.trim();


    // ADMINISTRADOR

    if (
        usuario === "admin" &&
        clave === "1234"
    ) {

        window.location.href =
            "/dashboard/";

        return;

    }


    // USUARIOS LOCALES

    const usuarios = JSON.parse(
        localStorage.getItem("usuarios")
    ) || [];


    const encontrado =
        usuarios.find(u =>

            u.usuario === usuario &&
            u.clave === clave

        );


    if (encontrado) {

        window.location.href =
            "/dashboard/";

    } else {

        mostrarNotificacion(
            "Usuario o contraseña incorrectos.",
            "error"
        );

    }

}


// =========================================
// REGISTRARSE
// =========================================

function registrarse() {

    alert(
        "El módulo de registro aún no está disponible."
    );

}


// =========================================
// ENTER PARA INICIAR SESIÓN
// =========================================

document.addEventListener(
    "keydown",
    function (e) {

        if (e.key === "Enter") {

            iniciarSesion();

        }

    }
);