
document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTOS
    // =========================================================

    const btnNuevoEmpleado = document.getElementById("btnNuevoEmpleado");
    const modalEmpleado = document.getElementById("modalEmpleado");
    const cerrarModal = document.getElementById("cerrarModal");
    const cancelarEmpleado = document.getElementById("cancelarEmpleado");

    const buscarEmpleado = document.getElementById("buscarEmpleado");
    const tablaEmpleados = document.getElementById("tablaEmpleados");

    const btnActualizar = document.getElementById("btnActualizar");
    const btnImprimir = document.getElementById("btnImprimir");


    // =========================================================
// ABRIR MODAL NUEVO EMPLEADO
// =========================================================

if (btnNuevoEmpleado && modalEmpleado) {

    btnNuevoEmpleado.onclick = function (event) {

        event.preventDefault();
        event.stopPropagation();

        console.log("BOTÓN NUEVO EMPLEADO FUNCIONANDO");

        modalEmpleado.style.display = "flex";
        modalEmpleado.style.visibility = "visible";
        modalEmpleado.style.opacity = "1";
        modalEmpleado.style.pointerEvents = "auto";
        modalEmpleado.style.zIndex = "99999";

        document.body.style.overflow = "hidden";

    };

}


    // =========================================================
    // CERRAR MODAL
    // =========================================================

    function cerrarModalEmpleado() {

    if (!modalEmpleado) {
        return;
    }

    modalEmpleado.style.display = "none";
    modalEmpleado.style.visibility = "hidden";
    modalEmpleado.style.opacity = "0";
    modalEmpleado.style.pointerEvents = "none";

    document.body.style.overflow = "";

}


    // =========================================================
    // BOTÓN X
    // =========================================================

    if (cerrarModal) {

        cerrarModal.addEventListener("click", function (event) {

            event.preventDefault();

            cerrarModalEmpleado();

        });

    }


    // =========================================================
    // BOTÓN CANCELAR
    // =========================================================

    if (cancelarEmpleado) {

        cancelarEmpleado.addEventListener("click", function (event) {

            event.preventDefault();

            cerrarModalEmpleado();

        });

    }


    // =========================================================
    // CLICK FUERA DEL MODAL
    // =========================================================

    if (modalEmpleado) {

        modalEmpleado.addEventListener("click", function (event) {

            if (event.target === modalEmpleado) {

                cerrarModalEmpleado();

            }

        });

    }


    // =========================================================
    // ESC
    // =========================================================

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            cerrarModalEmpleado();

        }

    });


    // =========================================================
    // BUSCADOR
    // =========================================================

    if (buscarEmpleado && tablaEmpleados) {

        buscarEmpleado.addEventListener("input", function () {

            const texto = this.value
                .toLowerCase()
                .trim();

            const filas = tablaEmpleados.querySelectorAll(
                "tr:not(.fila-vacia)"
            );

            let encontrados = 0;

            filas.forEach(function (fila) {

                const contenido = fila.textContent
                    .toLowerCase();

                if (contenido.includes(texto)) {

                    fila.style.display = "";

                    encontrados++;

                } else {

                    fila.style.display = "none";

                }

            });

            actualizarContadores(encontrados);

        });

    }


    // =========================================================
    // CONTADORES
    // =========================================================

    function actualizarContadores(cantidad) {

        const totalRegistros =
            document.getElementById("totalRegistros");

        const contadorTabla =
            document.getElementById("contadorTabla");

        const texto =
            cantidad === 1
                ? "1 registro"
                : cantidad + " registros";

        if (totalRegistros) {

            totalRegistros.textContent = texto;

        }

        if (contadorTabla) {

            contadorTabla.textContent = texto;

        }

    }


    // =========================================================
    // ESTADÍSTICAS
    // =========================================================

    function calcularEstadisticas() {

        if (!tablaEmpleados) {
            return;
        }

        const filas = tablaEmpleados.querySelectorAll(
            "tr:not(.fila-vacia)"
        );

        let total = 0;
        let activos = 0;
        let vacaciones = 0;

        filas.forEach(function (fila) {

            if (fila.style.display === "none") {
                return;
            }

            total++;

            const estado =
                fila.querySelector(".estado");

            if (estado) {

                const textoEstado =
                    estado.textContent
                        .trim()
                        .toLowerCase();

                if (textoEstado === "activo") {

                    activos++;

                }

                if (textoEstado === "vacaciones") {

                    vacaciones++;

                }

            }

        });


        const totalEmpleados =
            document.getElementById("totalEmpleados");

        const empleadosActivos =
            document.getElementById("empleadosActivos");

        const empleadosVacaciones =
            document.getElementById("empleadosVacaciones");


        if (totalEmpleados) {

            totalEmpleados.textContent = total;

        }

        if (empleadosActivos) {

            empleadosActivos.textContent = activos;

        }

        if (empleadosVacaciones) {

            empleadosVacaciones.textContent = vacaciones;

        }

    }


    // =========================================================
    // ELIMINAR EMPLEADO
    // =========================================================
    // El borrado ahora se hace con un <form method="post"> y token
    // CSRF desde la plantilla. Ya no hace falta JavaScript aqui.



    // =========================================================
    // ACTUALIZAR
    // =========================================================

    if (btnActualizar) {

        btnActualizar.addEventListener("click", function () {

            window.location.reload();

        });

    }


    // =========================================================
    // IMPRIMIR
    // =========================================================

    if (btnImprimir) {

        btnImprimir.addEventListener("click", function () {

            window.print();

        });

    }


    // =========================================================
    // INICIALIZAR
    // =========================================================

    calcularEstadisticas();

});