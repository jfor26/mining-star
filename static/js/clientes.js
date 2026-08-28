document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTOS
    // =========================================================

    const btnNuevoCliente =
        document.getElementById("btnNuevoCliente");

    const modalCliente =
        document.getElementById("modalCliente");

    const cerrarModal =
        document.getElementById("cerrarModal");

    const cancelarCliente =
        document.getElementById("cancelarCliente");

    const buscarCliente =
        document.getElementById("buscarCliente");

    const tablaClientes =
        document.getElementById("tablaClientes");

    const btnImprimir =
        document.getElementById("btnImprimir");

    const btnActualizar =
        document.getElementById("btnActualizar");


    // =========================================================
    // MODAL NUEVO CLIENTE
    // =========================================================

    if (btnNuevoCliente && modalCliente) {

        btnNuevoCliente.addEventListener(
            "click",
            function () {

                modalCliente.style.display = "flex";

                document.body.style.overflow = "hidden";

            }
        );

    }


    // =========================================================
    // CERRAR MODAL - X
    // =========================================================

    if (cerrarModal && modalCliente) {

        cerrarModal.addEventListener(
            "click",
            function () {

                modalCliente.style.display = "none";

                document.body.style.overflow = "";

            }
        );

    }


    // =========================================================
    // CERRAR MODAL - CANCELAR
    // =========================================================

    if (cancelarCliente && modalCliente) {

        cancelarCliente.addEventListener(
            "click",
            function () {

                modalCliente.style.display = "none";

                document.body.style.overflow = "";

            }
        );

    }


    // =========================================================
    // CERRAR MODAL AL HACER CLICK FUERA
    // =========================================================

    if (modalCliente) {

        modalCliente.addEventListener(
            "click",
            function (event) {

                if (event.target === modalCliente) {

                    modalCliente.style.display = "none";

                    document.body.style.overflow = "";

                }

            }
        );

    }


    // =========================================================
    // ESC PARA CERRAR MODAL
    // =========================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modalCliente
            ) {

                modalCliente.style.display = "none";

                document.body.style.overflow = "";

            }

        }
    );


    // =========================================================
    // ESTADÍSTICAS
    // =========================================================

    function actualizarEstadisticas() {

        if (!tablaClientes) {
            return;
        }


        const filas =
            tablaClientes.querySelectorAll(
                "tr:not(.fila-vacia)"
            );


        let total = 0;
        let activos = 0;
        let inactivos = 0;


        filas.forEach(function (fila) {

            if (fila.style.display === "none") {
                return;
            }


            total++;


            const estado =
                fila.querySelector(
                    ".estado-cliente"
                );


            if (estado) {

                const texto =
                    estado.textContent
                        .trim()
                        .toLowerCase();


                if (texto === "activo") {

                    activos++;

                }


                if (texto === "inactivo") {

                    inactivos++;

                }

            }

        });


        const totalClientes =
            document.getElementById(
                "totalClientes"
            );

        const clientesActivos =
            document.getElementById(
                "clientesActivos"
            );

        const clientesInactivos =
            document.getElementById(
                "clientesInactivos"
            );

        const totalRegistros =
            document.getElementById(
                "totalRegistros"
            );


        if (totalClientes) {

            totalClientes.textContent =
                total;

        }


        if (clientesActivos) {

            clientesActivos.textContent =
                activos;

        }


        if (clientesInactivos) {

            clientesInactivos.textContent =
                inactivos;

        }


        if (totalRegistros) {

            totalRegistros.textContent =
                total +
                (
                    total === 1
                        ? " registro"
                        : " registros"
                );

        }

    }


    // =========================================================
    // BUSCADOR
    // =========================================================

    if (buscarCliente && tablaClientes) {

        buscarCliente.addEventListener(
            "input",
            function () {

                const texto =
                    this.value
                        .toLowerCase()
                        .trim();


                const filas =
                    tablaClientes.querySelectorAll(
                        "tr:not(.fila-vacia)"
                    );


                let encontrados = 0;


                filas.forEach(function (fila) {

                    const contenido =
                        fila.textContent
                            .toLowerCase();


                    if (
                        contenido.includes(texto)
                    ) {

                        fila.style.display = "";

                        encontrados++;

                    } else {

                        fila.style.display = "none";

                    }

                });


                if (totalRegistros) {

                    totalRegistros.textContent =
                        encontrados +
                        (
                            encontrados === 1
                                ? " registro"
                                : " registros"
                        );

                }

            }
        );

    }


    // =========================================================
    // CONFIRMAR ELIMINACIÓN
    // =========================================================

    document.addEventListener(
        "click",
        function (event) {

            const boton =
                event.target.closest(
                    ".btn-delete"
                );


            if (!boton) {
                return;
            }


            const url =
                boton.getAttribute("href");


            if (!url) {
                return;
            }


            event.preventDefault();

            event.stopPropagation();


            const confirmar =
                window.confirm(
                    "¿Está seguro de eliminar este cliente?\n\n" +
                    "Esta acción no se puede deshacer."
                );


            if (confirmar) {

                window.location.assign(url);

            }

        }
    );


    // =========================================================
    // EDITAR CLIENTE
    // =========================================================

    document.addEventListener(
        "click",
        function (event) {

            const boton =
                event.target.closest(
                    ".btn-edit"
                );


            if (!boton) {
                return;
            }


            const url =
                boton.getAttribute("href");


            if (!url) {
                return;
            }


            event.preventDefault();

            event.stopPropagation();


            window.location.assign(url);

        }
    );


    // =========================================================
    // ACTUALIZAR
    // =========================================================

    if (btnActualizar) {

        btnActualizar.addEventListener(
            "click",
            function () {

                window.location.reload();

            }
        );

    }


    // =========================================================
    // IMPRIMIR CLIENTES
    // =========================================================

    if (btnImprimir) {

        btnImprimir.addEventListener(
            "click",
            function () {

                if (!tablaClientes) {
                    return;
                }


                // =============================================
                // OBTENER FILAS VISIBLES
                // =============================================

                const filas =
                    tablaClientes.querySelectorAll(
                        "tr:not(.fila-vacia)"
                    );


                let filasHTML = "";

                let cantidad = 0;


                filas.forEach(function (fila) {

                    if (
                        fila.style.display === "none"
                    ) {
                        return;
                    }


                    const celdas =
                        fila.querySelectorAll("td");


                    if (celdas.length < 7) {
                        return;
                    }


                    cantidad++;


                    filasHTML += `

                        <tr>

                            <td>
                                ${celdas[0].innerHTML}
                            </td>

                            <td>
                                ${celdas[1].innerHTML}
                            </td>

                            <td>
                                ${celdas[2].innerHTML}
                            </td>

                            <td>
                                ${celdas[3].innerHTML}
                            </td>

                            <td>
                                ${celdas[4].innerHTML}
                            </td>

                            <td>
                                ${celdas[5].innerHTML}
                            </td>

                        </tr>

                    `;

                });


                const textoRegistros =
                    cantidad === 1
                        ? "1 registro"
                        : cantidad + " registros";


                // =============================================
                // VENTANA DE IMPRESIÓN
                // =============================================

                const ventana =
                    window.open(
                        "",
                        "_blank",
                        "width=1200,height=800"
                    );


                if (!ventana) {

                    alert(
                        "El navegador bloqueó la ventana de impresión. " +
                        "Permite las ventanas emergentes para este sitio."
                    );

                    return;

                }


                ventana.document.write(`

                    <!DOCTYPE html>

                    <html lang="es">

                    <head>

                        <meta charset="UTF-8">

                        <title>
                            Clientes | Mining Star ERP
                        </title>


                        <style>

                            @page {

                                size: landscape;

                                margin: 10mm;

                            }


                            * {

                                box-sizing: border-box;

                            }


                            html,
                            body {

                                margin: 0;

                                padding: 0;

                                background: white;

                                font-family:
                                    Arial,
                                    Helvetica,
                                    sans-serif;

                                color: #222;

                            }


                            /* =================================
                               ENCABEZADO
                            ================================= */

                            .encabezado {

                                text-align: center;

                                margin-bottom: 18px;

                            }


                            .encabezado h1 {

                                margin: 0;

                                font-size: 24px;

                                font-weight: 700;

                                color: #123456;

                            }


                            .encabezado p {

                                margin: 5px 0 0;

                                font-size: 12px;

                                color: #555;

                            }


                            /* =================================
                               INFORMACIÓN
                            ================================= */

                            .tabla-header {

                                display: flex;

                                justify-content:
                                    space-between;

                                align-items: center;

                                padding: 7px 0;

                                margin-bottom: 7px;

                                border-bottom:
                                    2px solid #123456;

                            }


                            .tabla-header h2 {

                                margin: 0;

                                font-size: 16px;

                                color: #123456;

                            }


                            .tabla-header span {

                                font-size: 11px;

                                color: #555;

                            }


                            /* =================================
                               TABLA
                            ================================= */

                            table {

                                width: 100%;

                                border-collapse: collapse;

                                font-size: 10px;

                            }


                            thead {

                                display: table-header-group;

                            }


                            thead tr {

                                background: #123456;

                                color: white;

                            }


                            th {

                                padding: 7px 5px;

                                border:
                                    1px solid #777;

                                background: #123456;

                                color: white;

                                font-size: 10px;

                                font-weight: bold;

                                text-align: center;

                            }


                            td {

                                padding: 6px 5px;

                                border:
                                    1px solid #aaa;

                                background: white;

                                color: #222;

                                font-size: 10px;

                                text-align: center;

                            }


                            tr {

                                page-break-inside: avoid;

                                break-inside: avoid;

                            }


                            /* =================================
                               ESTADO
                            ================================= */

                            .estado-cliente {

                                background: transparent !important;

                                color: #222 !important;

                                padding: 0 !important;

                                border: none !important;

                            }


                            /* =================================
                               PIE
                            ================================= */

                            .pie {

                                margin-top: 12px;

                                padding-top: 6px;

                                border-top:
                                    1px solid #ccc;

                                text-align: right;

                                font-size: 9px;

                                color: #777;

                            }


                            @media print {

                                body {

                                    -webkit-print-color-adjust:
                                        exact;

                                    print-color-adjust:
                                        exact;

                                }

                            }

                        </style>

                    </head>


                    <body>


                        <div class="encabezado">

                            <h1>
                                Gestión de Clientes
                            </h1>

                            <p>
                                Administre la información
                                de todos los clientes
                                de Mining Star ERP.
                            </p>

                        </div>


                        <div class="tabla-header">

                            <h2>
                                Lista de Clientes
                            </h2>

                            <span>
                                ${textoRegistros}
                            </span>

                        </div>


                        <table>

                            <thead>

                                <tr>

                                    <th>
                                        Documento
                                    </th>

                                    <th>
                                        Nombre
                                    </th>

                                    <th>
                                        Empresa
                                    </th>

                                    <th>
                                        Correo
                                    </th>

                                    <th>
                                        Teléfono
                                    </th>

                                    <th>
                                        Estado
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                ${filasHTML}

                            </tbody>

                        </table>


                        <div class="pie">

                            Mining Star ERP |
                            Sistema Integral de Gestión Minera

                        </div>


                    </body>

                    </html>

                `);


                ventana.document.close();


                ventana.focus();


                setTimeout(
                    function () {

                        ventana.print();

                    },
                    500
                );

            }
        );

    }


    // =========================================================
    // INICIALIZAR
    // =========================================================

    actualizarEstadisticas();

});