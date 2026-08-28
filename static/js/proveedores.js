document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // ELEMENTOS DEL MODAL
    // ==========================================

    const btnNuevoProveedor =
        document.getElementById("btnNuevoProveedor");

    const modalProveedor =
        document.getElementById("modalProveedor");

    const cerrarModalProveedor =
        document.getElementById("cerrarModalProveedor");

    const cancelarProveedor =
        document.getElementById("cancelarProveedor");


    // ==========================================
    // ABRIR MODAL
    // ==========================================

    if (btnNuevoProveedor && modalProveedor) {

        btnNuevoProveedor.addEventListener("click", function () {

            modalProveedor.style.display = "flex";

            document.body.style.overflow = "hidden";

            // Colocar el cursor en el NIT
            const nit = document.getElementById("nit");

            if (nit) {
                setTimeout(function () {
                    nit.focus();
                }, 100);
            }

        });

    }


    // ==========================================
    // CERRAR MODAL - X
    // ==========================================

    if (cerrarModalProveedor && modalProveedor) {

        cerrarModalProveedor.addEventListener("click", function () {

            modalProveedor.style.display = "none";

            document.body.style.overflow = "";

        });

    }


    // ==========================================
    // CERRAR MODAL - CANCELAR
    // ==========================================

    if (cancelarProveedor && modalProveedor) {

        cancelarProveedor.addEventListener("click", function () {

            modalProveedor.style.display = "none";

            document.body.style.overflow = "";

        });

    }


    // ==========================================
    // CERRAR AL HACER CLICK FUERA DEL MODAL
    // ==========================================

    if (modalProveedor) {

        modalProveedor.addEventListener("click", function (event) {

            if (event.target === modalProveedor) {

                modalProveedor.style.display = "none";

                document.body.style.overflow = "";

            }

        });

    }


    // ==========================================
    // CERRAR CON ESC
    // ==========================================

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape" && modalProveedor) {

            modalProveedor.style.display = "none";

            document.body.style.overflow = "";

        }

    });


    // ==========================================
    // BUSCADOR DE PROVEEDORES
    // ==========================================

    const buscador =
        document.getElementById("buscarProveedor");

    const tabla =
        document.getElementById("tablaProveedores");

    const contador =
        document.getElementById("totalRegistros");


    if (buscador && tabla) {

        buscador.addEventListener("input", function () {

            const texto =
                this.value.toLowerCase().trim();

            const filas =
                tabla.querySelectorAll("tr");

            let encontrados = 0;


            filas.forEach(function (fila) {

                if (fila.querySelector(".empty")) {
                    return;
                }

                const contenido =
                    fila.textContent.toLowerCase();


                if (contenido.includes(texto)) {

                    fila.style.display = "";

                    encontrados++;

                } else {

                    fila.style.display = "none";

                }

            });


            // ==========================================
            // ACTUALIZAR CONTADOR
            // ==========================================

            if (contador) {

                contador.textContent =
                    encontrados +
                    (
                        encontrados === 1
                            ? " registro"
                            : " registros"
                    );

            }


            // ==========================================
            // MENSAJE SIN RESULTADOS
            // ==========================================

            let mensaje =
                document.getElementById(
                    "mensajeSinResultados"
                );


            if (encontrados === 0 && texto !== "") {

                if (!mensaje) {

                    mensaje =
                        document.createElement("tr");

                    mensaje.id =
                        "mensajeSinResultados";


                    mensaje.innerHTML = `
                        <td colspan="8" class="empty">

                            <i class="fa-solid fa-magnifying-glass"></i>

                            <p>
                                No se encontraron proveedores.
                            </p>

                        </td>
                    `;


                    tabla.appendChild(mensaje);

                }

            } else {

                if (mensaje) {

                    mensaje.remove();

                }

            }

        });

    }


    // ==========================================
    // BOTÓN ACTUALIZAR
    // ==========================================

    const btnActualizar =
        document.getElementById("btnActualizar");


    if (btnActualizar) {

        btnActualizar.addEventListener("click", function () {

            location.reload();

        });

    }


    // ==========================================
    // BOTÓN IMPRIMIR
    // ==========================================

    const btnImprimir =
        document.getElementById("btnImprimir");


    if (btnImprimir) {

        btnImprimir.addEventListener("click", function () {

            window.print();

        });

    }


});