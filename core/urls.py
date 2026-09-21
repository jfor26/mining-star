"""
Rutas de la aplicacion core.

Los nombres (name="...") se conservan igual que antes para no romper
ningun {% url %} de las plantillas. Lo que cambia es que las rutas de
borrado ahora solo aceptan POST (ver las vistas correspondientes).
"""

from django.urls import path

from . import views

urlpatterns = [
    # ==========================================
    # AUTENTICACION
    # ==========================================
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ==========================================
    # DASHBOARD
    # ==========================================
    path("dashboard/", views.dashboard, name="dashboard"),

    # ==========================================
    # EMPLEADOS
    # ==========================================
    path("empleados/", views.empleados, name="empleados"),
    path("empleados/editar/<int:id>/", views.editar_empleado, name="editar_empleado"),
    path("empleados/eliminar/<int:id>/", views.eliminar_empleado, name="eliminar_empleado"),
    path("empleados/exportar/", views.exportar_empleados_excel, name="exportar_empleados_excel"),
    path("empleados/pdf/", views.exportar_empleados_pdf, name="exportar_empleados_pdf"),

    # ==========================================
    # CLIENTES
    # ==========================================
    path("clientes/", views.clientes, name="clientes"),
    path("clientes/editar/<int:id>/", views.editar_cliente, name="editar_cliente"),
    path("clientes/eliminar/<int:id>/", views.eliminar_cliente, name="eliminar_cliente"),
    path("clientes/exportar/", views.exportar_clientes_excel, name="exportar_clientes_excel"),
    path("clientes/pdf/", views.exportar_clientes_pdf, name="exportar_clientes_pdf"),

    # ==========================================
    # PRODUCTOS
    # ==========================================
    path("productos/", views.productos, name="productos"),
    path("productos/nuevo/", views.nuevo_producto, name="nuevo_producto"),
    path("productos/editar/<int:id>/", views.editar_producto, name="editar_producto"),
    path("productos/eliminar/<int:id>/", views.eliminar_producto, name="eliminar_producto"),
    path("productos/exportar/", views.exportar_productos_excel, name="exportar_productos_excel"),
    path("productos/pdf/", views.exportar_productos_pdf, name="exportar_productos_pdf"),

    # ==========================================
    # PROVEEDORES
    # ==========================================
    path("proveedores/", views.proveedores, name="proveedores"),
    path("proveedores/editar/<int:id>/", views.editar_proveedor, name="editar_proveedor"),
    path("proveedores/eliminar/<int:id>/", views.eliminar_proveedor, name="eliminar_proveedor"),
    path("proveedores/exportar/", views.exportar_proveedores_excel, name="exportar_proveedores_excel"),
    path("proveedores/pdf/", views.exportar_proveedores_pdf, name="exportar_proveedores_pdf"),

    # ==========================================
    # VENTAS
    # ==========================================
    path("ventas/", views.ventas, name="ventas"),
    path("ventas/eliminar/<int:id>/", views.eliminar_venta, name="eliminar_venta"),

    # ==========================================
    # PRODUCCION DIARIA (HU-001)
    # ==========================================
    path("produccion/", views.produccion, name="produccion"),
    path("produccion/eliminar/<int:id>/", views.eliminar_produccion, name="eliminar_produccion"),

    # ==========================================
    # REPORTES
    # ==========================================
    path("reportes/", views.reportes, name="reportes"),
]
