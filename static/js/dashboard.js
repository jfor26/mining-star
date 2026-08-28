// =========================================================
// MINING STAR ERP
// DASHBOARD.JS
// =========================================================
 
document.addEventListener("DOMContentLoaded", function () {
 
 
    // =====================================================
    // FECHA ACTUAL
    // =====================================================
 
    const fechaActual =
        document.getElementById("fechaActual");
 
    if (fechaActual) {
 
        const opciones = {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
        };
 
        const hoy = new Date();
 
        fechaActual.textContent =
            hoy.toLocaleDateString(
                "es-CO",
                opciones
            );
    }
 
 
    // =====================================================
    // SALUDO DINÁMICO
    // =====================================================
 
    const titulo =
        document.querySelector(
            ".welcome-info h1"
        );
 
    if (titulo) {
 
        const hora =
            new Date().getHours();
 
        if (hora < 12) {
 
            titulo.textContent =
                "☀️ Buenos días, Administrador";
 
        } else if (hora < 18) {
 
            titulo.textContent =
                "🌤️ Buenas tardes, Administrador";
 
        } else {
 
            titulo.textContent =
                "🌙 Buenas noches, Administrador";
 
        }
    }
 
 
    // =====================================================
    // CONTADORES ANIMADOS
    // =====================================================
 
    function animarContador(
        id,
        valor
    ) {
 
        const contador =
            document.getElementById(id);
 
        if (!contador) {
            return;
        }
 
        let inicio = 0;
 
        const duracion = 1000;
 
        const pasos = 50;
 
        const incremento =
            valor / pasos;
 
        const intervalo =
            duracion / pasos;
 
        const timer =
            setInterval(function () {
 
                inicio += incremento;
 
                if (inicio >= valor) {
 
                    inicio = valor;
 
                    clearInterval(timer);
                }
 
                contador.textContent =
                    Math.floor(inicio);
 
            }, intervalo);
    }
 
 
    animarContador(
        "totalEmpleados",
        128
    );
 
    animarContador(
        "totalClientes",
        580
    );
 
    animarContador(
        "totalProductos",
        94
    );
 
    animarContador(
        "totalProveedores",
        21
    );
 
 
    // =====================================================
    // GRÁFICO DE VENTAS
    // =====================================================
 
    const canvas =
        document.getElementById(
            "graficoVentas"
        );
 
 
    if (
        canvas &&
        typeof Chart !== "undefined"
    ) {
 
        new Chart(
            canvas,
            {
 
                type: "bar",
 
                data: {
 
                    labels: [
                        "Ene",
                        "Feb",
                        "Mar",
                        "Abr",
                        "May",
                        "Jun",
                        "Jul",
                        "Ago",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dic"
                    ],
 
                    datasets: [
 
                        {
 
                            label: "Ventas",
 
                            data: [
                                12,
                                18,
                                14,
                                22,
                                25,
                                27,
                                30,
                                28,
                                32,
                                35,
                                40,
                                45
                            ],
 
                            backgroundColor:
                                "#2563eb",
 
                            borderRadius: 8
 
                        }
 
                    ]
 
                },
 
                options: {
 
                    responsive: true,
 
                    maintainAspectRatio: false,
 
                    plugins: {
 
                        legend: {
 
                            display: false
 
                        }
 
                    },
 
                    scales: {
 
                        y: {
 
                            beginAtZero: true
 
                        }
 
                    }
 
                }
 
            }
        );
 
    }
 
 
    // =====================================================
    // FUNCIÓN DE NAVEGACIÓN
    // =====================================================
 
    function irA(url) {
 
        if (!url) {
            return;
        }
 
        window.location.href = url;
 
    }
 
 
    // =====================================================
    // VER REPORTE DE VENTAS
    // =====================================================
 
    const btnReporteVentas =
        document.getElementById(
            "btnReporteVentas"
        );
 
    if (btnReporteVentas) {
 
        btnReporteVentas.addEventListener(
            "click",
            function () {
 
                irA(
                    "/reportes/"
                );
 
            }
        );
 
    }
 
 
    // =====================================================
    // MENÚ SIDEBAR
    // =====================================================
 
 
    // -----------------------------------------------------
    // CLIENTES
    // -----------------------------------------------------
 
    const menuClientes =
        document.getElementById(
            "menuClientes"
        );
 
    if (menuClientes) {
 
        menuClientes.addEventListener(
            "click",
            function (event) {
 
                event.preventDefault();
 
                irA(
                    "/clientes/"
                );
 
            }
        );
 
    }
 
 
    // -----------------------------------------------------
    // PRODUCTOS
    // -----------------------------------------------------
 
    const menuProductos =
        document.getElementById(
            "menuProductos"
        );
 
    if (menuProductos) {
 
        menuProductos.addEventListener(
            "click",
            function (event) {
 
                event.preventDefault();
 
                irA(
                    "/productos/"
                );
 
            }
        );
 
    }
 
 
    // -----------------------------------------------------
    // PROVEEDORES
    // -----------------------------------------------------
 
    const menuProveedores =
        document.getElementById(
            "menuProveedores"
        );
 
    if (menuProveedores) {
 
        menuProveedores.addEventListener(
            "click",
            function (event) {
 
                event.preventDefault();
 
                irA(
                    "/proveedores/"
                );
 
            }
        );
 
    }
 
 
    // -----------------------------------------------------
    // VENTAS
    // -----------------------------------------------------
 
    const menuVentas =
        document.getElementById(
            "menuVentas"
        );
 
    if (menuVentas) {
 
        menuVentas.addEventListener(
            "click",
            function (event) {
 
                event.preventDefault();
 
                irA(
                    "/ventas/"
                );
 
            }
        );
 
    }
 
 
    // -----------------------------------------------------
    // REPORTES
    // -----------------------------------------------------
 
    const menuReportes =
        document.getElementById(
            "menuReportes"
        );
 
    if (menuReportes) {
 
        menuReportes.addEventListener(
            "click",
            function (event) {
 
                event.preventDefault();
 
                irA(
                    "/reportes/"
                );
 
            }
        );
 
    }
 
 
    // =====================================================
    // CONFIGURACIÓN
    // =====================================================
 
    const menuConfiguracion =
        document.getElementById(
            "menuConfiguracion"
        );
 
    if (menuConfiguracion) {
 
        menuConfiguracion.addEventListener(
            "click",
            function (event) {
 
                event.preventDefault();
 
                alert(
                    "El módulo de Configuración estará disponible próximamente."
                );
 
            }
        );
 
    }
 
 
    // =====================================================
    // NOTIFICACIONES
    // =====================================================
 
    const btnNotificaciones =
        document.getElementById(
            "btnNotificaciones"
        );
 
    if (btnNotificaciones) {
 
        btnNotificaciones.addEventListener(
            "click",
            function () {
 
                alert(
                    "Tienes 3 notificaciones nuevas."
                );
 
            }
        );
 
    }
 
 
    // =====================================================
    // MENSAJES
    // =====================================================
 
    const btnMensajes =
        document.getElementById(
            "btnMensajes"
        );
 
    if (btnMensajes) {
 
        btnMensajes.addEventListener(
            "click",
            function () {
 
                alert(
                    "No tienes mensajes pendientes."
                );
 
            }
        );
 
    }
 
 
    // =====================================================
    // CONFIGURACIÓN TOPBAR
    // =====================================================
 
    const btnConfiguracion =
        document.getElementById(
            "btnConfiguracion"
        );
 
    if (btnConfiguracion) {
 
        btnConfiguracion.addEventListener(
            "click",
            function () {
 
                alert(
                    "El módulo de Configuración estará disponible próximamente."
                );
 
            }
        );
 
    }
 
 
    // =====================================================
    // CERRAR SESIÓN
    // =====================================================
 
    const btnCerrarSesion =
        document.getElementById(
            "btnCerrarSesion"
        );
 
    if (btnCerrarSesion) {
 
        btnCerrarSesion.addEventListener(
            "click",
            function (event) {
 
                const confirmar =
                    window.confirm(
                        "¿Está seguro de cerrar la sesión?"
                    );
 
                if (!confirmar) {
 
                    event.preventDefault();
 
                }
 
            }
        );
 
    }
 
 
    // =====================================================
    // EFECTO TARJETAS KPI
    // =====================================================
 
    const tarjetas =
        document.querySelectorAll(
            ".stat-card"
        );
 
 
    tarjetas.forEach(
        function (card) {
 
            card.addEventListener(
                "mouseenter",
                function () {
 
                    card.style.transform =
                        "translateY(-8px) scale(1.03)";
 
                }
            );
 
 
            card.addEventListener(
                "mouseleave",
                function () {
 
                    card.style.transform =
                        "translateY(0) scale(1)";
 
                }
            );
 
        }
    );
 
 
    // =====================================================
    // RELOJ
    // =====================================================
 
    const topbarRight =
        document.querySelector(
            ".topbar-right"
        );
 
 
    if (topbarRight) {
 
        const reloj =
            document.createElement(
                "div"
            );
 
 
        reloj.className =
            "reloj-dashboard";
 
 
        reloj.style.fontWeight =
            "600";
 
 
        reloj.style.color =
            "#64748b";
 
 
        reloj.style.marginRight =
            "10px";
 
 
        topbarRight.prepend(
            reloj
        );
 
 
        function actualizarReloj() {
 
            const ahora =
                new Date();
 
 
            reloj.textContent =
                ahora.toLocaleTimeString(
                    "es-CO"
                );
 
        }
 
 
        actualizarReloj();
 
 
        setInterval(
            actualizarReloj,
            1000
        );
 
    }
 
 
    // =====================================================
    // BUSCADOR
    // =====================================================
 
    const buscador =
        document.getElementById(
            "buscadorDashboard"
        );
 
 
    if (buscador) {
 
        buscador.addEventListener(
            "keydown",
            function (event) {
 
                if (
                    event.key === "Enter"
                ) {
 
                    const texto =
                        buscador.value
                            .trim()
                            .toLowerCase();
 
 
                    if (!texto) {
                        return;
                    }
 
 
                    if (
                        texto.includes(
                            "empleado"
                        )
                    ) {
 
                        irA(
                            "/empleados/"
                        );
 
                    } else if (
                        texto.includes(
                            "cliente"
                        )
                    ) {
 
                        irA(
                            "/clientes/"
                        );
 
                    } else if (
                        texto.includes(
                            "producto"
                        )
                    ) {
 
                        irA(
                            "/productos/"
                        );
 
                    } else if (
                        texto.includes(
                            "proveedor"
                        )
                    ) {
 
                        irA(
                            "/proveedores/"
                        );
 
                    } else if (
                        texto.includes(
                            "venta"
                        )
                    ) {
 
                        irA(
                            "/ventas/"
                        );
 
                    } else if (
                        texto.includes(
                            "reporte"
                        )
                    ) {
 
                        irA(
                            "/reportes/"
                        );
 
                    } else {
 
                        alert(
                            "No se encontró un módulo relacionado con: " +
                            buscador.value
                        );
 
                    }
 
                }
 
            }
        );
 
    }
 
 
    // =====================================================
    // MENSAJE DE INICIO
    // =====================================================
 
    console.log(
        "Mining Star ERP - Dashboard iniciado correctamente."
    );
 
});
 
 
// ==========================================================
// ACCIONES RÁPIDAS - DASHBOARD
// ==========================================================
 
document.addEventListener("DOMContentLoaded", function () {
 
    // -------- ELEMENTOS: MODAL EMPLEADO --------
    const modalEmpleado = document.getElementById("modalEmpleadoDash");
    const btnNuevoEmpleado = document.getElementById("btnNuevoEmpleado");
    const btnCerrar = document.getElementById("cerrarModalDash");
    const btnCancelar = document.getElementById("cancelarEmpleadoDash");
    const formEmpleado = document.getElementById("formEmpleadoDash");
 
    // -------- ELEMENTOS: MODAL CLIENTE --------
    const modalCliente = document.getElementById("modalClienteDash");
    const btnNuevoCliente = document.getElementById("btnNuevoCliente");
    const btnCerrarCliente = document.getElementById("cerrarModalClienteDash");
    const btnCancelarCliente = document.getElementById("cancelarClienteDash");
    const formCliente = document.getElementById("formClienteDash");

        // -------- ELEMENTOS: MODAL PRODUCTO --------
    const modalProducto = document.getElementById("modalProductoDash");
    const btnNuevoProducto = document.getElementById("btnNuevoProducto");
    const btnCerrarProducto = document.getElementById("cerrarModalProductoDash");
    const btnCancelarProducto = document.getElementById("cancelarProductoDash");
    const formProducto = document.getElementById("formProductoDash");

        // -------- ELEMENTOS: MODAL PROVEEDOR --------
    const modalProveedor = document.getElementById("modalProveedorDash");
    const btnNuevoProveedor = document.getElementById("btnNuevoProveedor");
    const btnCerrarProveedor = document.getElementById("cerrarModalProveedorDash");
    const btnCancelarProveedor = document.getElementById("cancelarProveedorDash");
    const formProveedor = document.getElementById("formProveedorDash");

        // -------- ELEMENTOS: MODAL VENTA --------
    const modalVentaDash = document.getElementById("modalVentaDash");
    const btnNuevaVenta = document.getElementById("btnNuevaVenta");
    const btnCerrarVentaDash = document.getElementById("cerrarModalVentaDash");
    const btnCancelarVentaDash = document.getElementById("cancelarVentaDash");
    const formVentaDash = document.getElementById("formVentaDash");
    const productoVentaDash = document.getElementById("productoVentaDash");
    const cantidadVentaDash = document.getElementById("cantidadVentaDash");
    const totalVentaDashPreview = document.getElementById("totalVentaDashPreview");
 
 
    // =====================================================
    // MODAL EMPLEADO
    // =====================================================
 
    if (btnNuevoEmpleado) {
        btnNuevoEmpleado.addEventListener("click", function () {
            modalEmpleado.style.display = "flex";
        });
    }
 
    function cerrarModalEmpleado() {
        modalEmpleado.style.display = "none";
        formEmpleado.reset();
    }
 
    if (btnCerrar) btnCerrar.addEventListener("click", cerrarModalEmpleado);
    if (btnCancelar) btnCancelar.addEventListener("click", cerrarModalEmpleado);
 
    if (formEmpleado) {
        formEmpleado.addEventListener("submit", function (e) {
            e.preventDefault();
 
            const formData = new FormData(formEmpleado);
 
            fetch(formEmpleado.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            })
                .then(response => response.json().then(data => ({ status: response.status, data })))
                .then(({ status, data }) => {
 
                    if (status === 200 && data.success) {
 
                        alert(data.message || "Empleado agregado correctamente.");
                        cerrarModalEmpleado();
 
                        const totalEmpleadosEl = document.getElementById("totalEmpleados");
                        if (totalEmpleadosEl) {
                            totalEmpleadosEl.textContent =
                                parseInt(totalEmpleadosEl.textContent || "0") + 1;
                        }
 
                    } else {
 
                        const primerError = data.errors
                            ? Object.values(data.errors)[0][0].message
                            : "Revisa los datos del formulario.";
                        alert("No se pudo guardar: " + primerError);
 
                    }
 
                })
                .catch(() => {
                    alert("Ocurrió un error al guardar el empleado. Intenta de nuevo.");
                });
        });
    }
 
 
    // =====================================================
    // MODAL CLIENTE
    // =====================================================
 
    if (btnNuevoCliente) {
        btnNuevoCliente.addEventListener("click", function () {
            modalCliente.style.display = "flex";
        });
    }
 
    function cerrarModalCliente() {
        modalCliente.style.display = "none";
        formCliente.reset();
    }
 
    if (btnCerrarCliente) btnCerrarCliente.addEventListener("click", cerrarModalCliente);
    if (btnCancelarCliente) btnCancelarCliente.addEventListener("click", cerrarModalCliente);
 
    if (formCliente) {
        formCliente.addEventListener("submit", function (e) {
            e.preventDefault();
 
            const formData = new FormData(formCliente);
 
            fetch(formCliente.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            })
                .then(response => response.json().then(data => ({ status: response.status, data })))
                .then(({ status, data }) => {
 
                    if (status === 200 && data.success) {
 
                        alert(data.message || "Cliente agregado correctamente.");
                        cerrarModalCliente();
 
                        const totalClientesEl = document.getElementById("totalClientes");
                        if (totalClientesEl) {
                            totalClientesEl.textContent =
                                parseInt(totalClientesEl.textContent || "0") + 1;
                        }
 
                    } else {
 
                        alert("No se pudo guardar el cliente. Revisa los datos.");
 
                    }
 
                })
                .catch(() => {
                    alert("Ocurrió un error al guardar el cliente. Intenta de nuevo.");
                });
        });
    }
        // =====================================================
    // MODAL PRODUCTO
    // =====================================================

    if (btnNuevoProducto) {
        btnNuevoProducto.addEventListener("click", function () {
            modalProducto.style.display = "flex";
        });
    }

    function cerrarModalProducto() {
        modalProducto.style.display = "none";
        formProducto.reset();
    }

    if (btnCerrarProducto) btnCerrarProducto.addEventListener("click", cerrarModalProducto);
    if (btnCancelarProducto) btnCancelarProducto.addEventListener("click", cerrarModalProducto);

    if (formProducto) {
        formProducto.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(formProducto);

            fetch(formProducto.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            })
                .then(response => response.json().then(data => ({ status: response.status, data })))
                .then(({ status, data }) => {

                    if (status === 200 && data.success) {

                        alert(data.message || "Producto registrado correctamente.");
                        cerrarModalProducto();

                        const totalProductosEl = document.getElementById("totalProductos");
                        if (totalProductosEl) {
                            totalProductosEl.textContent =
                                parseInt(totalProductosEl.textContent || "0") + 1;
                        }

                    } else {

                        alert("No se pudo guardar el producto. Revisa los datos.");

                    }

                })
                .catch(() => {
                    alert("Ocurrió un error al guardar el producto. Intenta de nuevo.");
                });
        });
    }

        // =====================================================
    // MODAL PROVEEDOR
    // =====================================================

    if (btnNuevoProveedor) {
        btnNuevoProveedor.addEventListener("click", function () {
            modalProveedor.style.display = "flex";
        });
    }

    function cerrarModalProveedor() {
        modalProveedor.style.display = "none";
        formProveedor.reset();
    }

    if (btnCerrarProveedor) btnCerrarProveedor.addEventListener("click", cerrarModalProveedor);
    if (btnCancelarProveedor) btnCancelarProveedor.addEventListener("click", cerrarModalProveedor);

    if (formProveedor) {
        formProveedor.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(formProveedor);

            fetch(formProveedor.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            })
                .then(response => response.json().then(data => ({ status: response.status, data })))
                .then(({ status, data }) => {

                    if (status === 200 && data.success) {

                        alert(data.message || "Proveedor agregado correctamente.");
                        cerrarModalProveedor();

                        const totalProveedoresEl = document.getElementById("totalProveedores");
                        if (totalProveedoresEl) {
                            totalProveedoresEl.textContent =
                                parseInt(totalProveedoresEl.textContent || "0") + 1;
                        }

                    } else {

                        alert("No se pudo guardar el proveedor. Revisa los datos.");

                    }

                })
                .catch(() => {
                    alert("Ocurrió un error al guardar el proveedor. Intenta de nuevo.");
                });
        });
    }
     // =====================================================
    // MODAL VENTA
    // =====================================================

    if (btnNuevaVenta) {
        btnNuevaVenta.addEventListener("click", function () {
            modalVentaDash.style.display = "flex";
        });
    }

    function cerrarModalVentaDash() {
        modalVentaDash.style.display = "none";
        formVentaDash.reset();
        totalVentaDashPreview.value = "$0";
    }

    if (btnCerrarVentaDash) btnCerrarVentaDash.addEventListener("click", cerrarModalVentaDash);
    if (btnCancelarVentaDash) btnCancelarVentaDash.addEventListener("click", cerrarModalVentaDash);

    function actualizarTotalVentaDash() {
        const opcion = productoVentaDash.options[productoVentaDash.selectedIndex];
        const precio = parseFloat(opcion.dataset.precio || 0);
        const cantidad = parseInt(cantidadVentaDash.value || 0);
        const total = precio * cantidad;
        totalVentaDashPreview.value = "$" + total.toLocaleString("es-CO");
    }

    if (productoVentaDash) productoVentaDash.addEventListener("change", actualizarTotalVentaDash);
    if (cantidadVentaDash) cantidadVentaDash.addEventListener("input", actualizarTotalVentaDash);

    if (formVentaDash) {
        formVentaDash.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(formVentaDash);

            fetch(formVentaDash.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            })
                .then(response => response.json().then(data => ({ status: response.status, data })))
                .then(({ status, data }) => {

                    if (status === 200 && data.success) {

                        alert(data.message || "Venta registrada correctamente.");
                        cerrarModalVentaDash();

                    } else {

                        alert("No se pudo guardar la venta. Revisa los datos.");

                    }

                })
                .catch(() => {
                    alert("Ocurrió un error al registrar la venta. Intenta de nuevo.");
                });
        });
    }
});