"""
Control de acceso por cargo (roles) de Mining Star.

Cada empleado que usa el sistema tiene un usuario de Django que pertenece a
UN grupo con el nombre de su cargo (Gerente, Supervisor, Comercial...). Lo
que cada cargo puede hacer en cada modulo se declara una sola vez en la
matriz MATRIZ_DE_ACCESO. De ahi la leen:

- la API REST (clase PermisoPorModulo), que decide si responde 403;
- el front-end, que recibe la matriz del usuario en /auth/perfil/ y oculta
  los menus y botones que no le corresponden.

Se eligio una matriz explicita en lugar de los permisos por modelo de Django
(add_cliente, change_cliente...) porque es mas facil de leer, de auditar y de
explicar: una fila por cargo, una columna por modulo.

Operaciones: "ver", "crear", "editar", "eliminar".
"""

from rest_framework.permissions import BasePermission

VER, CREAR, EDITAR, ELIMINAR = "ver", "crear", "editar", "eliminar"
TODO = frozenset({VER, CREAR, EDITAR, ELIMINAR})
LECTURA = frozenset({VER})

MODULOS = {
    "panel": "Panel de control",
    "clientes": "Clientes",
    "crm": "CRM (oportunidades e interacciones)",
    "proveedores": "Proveedores",
    "productos": "Productos e inventario",
    "empleados": "Empleados",
    "ventas": "Ventas",
    "pedidos": "Tienda, carrito y pagos",
    "produccion": "Producción de la mina",
    "normativa": "Requisitos mineros y ambientales",
    "mejora": "Mejora continua (PHVA)",
    "seguridad": "Seguridad: usuarios, accesos y respaldos",
}

# Fila = cargo. Columna = modulo. Un modulo ausente significa "sin acceso".
MATRIZ_DE_ACCESO = {
    "Administrador": dict.fromkeys(MODULOS, TODO),
    "Gerente": {
        "panel": LECTURA,
        "clientes": LECTURA,
        "crm": TODO,
        "proveedores": LECTURA,
        "productos": LECTURA,
        "empleados": LECTURA,
        "ventas": LECTURA,
        "pedidos": LECTURA,
        "produccion": LECTURA,
        "normativa": frozenset({VER, CREAR, EDITAR}),
        "mejora": frozenset({VER, CREAR, EDITAR}),
        "seguridad": LECTURA,
    },
    "Supervisor": {
        "panel": LECTURA,
        "productos": LECTURA,
        "empleados": LECTURA,
        "produccion": frozenset({VER, CREAR, EDITAR}),
        "normativa": frozenset({VER, CREAR, EDITAR}),
        "mejora": frozenset({VER, CREAR, EDITAR}),
    },
    "Comercial": {
        "panel": LECTURA,
        "clientes": frozenset({VER, CREAR, EDITAR}),
        "crm": TODO,
        "productos": LECTURA,
        "ventas": frozenset({VER, CREAR}),
        "pedidos": frozenset({VER, CREAR}),
        "mejora": frozenset({VER, CREAR}),
    },
    "Contador": {
        "panel": LECTURA,
        "clientes": LECTURA,
        "proveedores": frozenset({VER, CREAR, EDITAR}),
        "productos": LECTURA,
        "ventas": frozenset({VER, EDITAR}),
        "pedidos": LECTURA,
        "normativa": LECTURA,
        "mejora": frozenset({VER, CREAR}),
    },
    "Operario": {
        "panel": LECTURA,
        "produccion": frozenset({VER, CREAR}),
        "mejora": frozenset({VER, CREAR}),
    },
    "Auxiliar": {
        "panel": LECTURA,
        "clientes": LECTURA,
        "proveedores": LECTURA,
        "productos": frozenset({VER, CREAR, EDITAR}),
        "pedidos": LECTURA,
        "mejora": frozenset({VER, CREAR}),
    },
}

ROLES = list(MATRIZ_DE_ACCESO)

# Los clientes que entran al portal tienen su propio rol. No esta en la
# matriz porque no usan ningun modulo interno: solo la API /portal/, que
# ademas filtra todo por el cliente vinculado a su usuario.
ROL_CLIENTE = "Cliente"


def rol_de(usuario):
    """Devuelve el cargo del usuario o None si no tiene ninguno asignado.

    El superusuario de Django se trata como Administrador aunque no este en
    el grupo, para no quedar nunca fuera del sistema.
    """
    if not usuario or not usuario.is_authenticated:
        return None
    if usuario.is_superuser:
        return "Administrador"
    nombres = set(usuario.groups.values_list("name", flat=True))
    for rol in ROLES:  # orden de la matriz: el de mas privilegio gana
        if rol in nombres:
            return rol
    if ROL_CLIENTE in nombres:
        return ROL_CLIENTE
    return None


def permisos_de(usuario):
    """Matriz {modulo: [operaciones]} del usuario, lista para enviar como JSON."""
    rol = rol_de(usuario)
    if rol is None:
        return {}
    return {modulo: sorted(ops) for modulo, ops in MATRIZ_DE_ACCESO.get(rol, {}).items()}


def puede(usuario, modulo, operacion=VER):
    rol = rol_de(usuario)
    if rol is None:
        return False
    return operacion in MATRIZ_DE_ACCESO.get(rol, {}).get(modulo, frozenset())


# Accion de DRF -> operacion de la matriz.
OPERACION_POR_ACCION = {
    "list": VER,
    "retrieve": VER,
    "create": CREAR,
    "update": EDITAR,
    "partial_update": EDITAR,
    "destroy": ELIMINAR,
}


class PermisoPorModulo(BasePermission):
    """Permiso de DRF que consulta la matriz de acceso.

    La vista declara:
        modulo = "clientes"
        operaciones_por_accion = {"anular": "editar"}   # acciones propias

    Las acciones propias que no se declaren se tratan como lectura si son
    GET y como creacion en cualquier otro metodo.
    """

    message = "Su cargo no tiene permiso para realizar esta operacion en este modulo."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        modulo = getattr(view, "modulo", None)
        if modulo is None:
            return True  # vista sin modulo: basta con estar autenticado
        accion = getattr(view, "action", None)
        especiales = getattr(view, "operaciones_por_accion", {})
        if accion in especiales:
            operacion = especiales[accion]
        elif accion in OPERACION_POR_ACCION:
            operacion = OPERACION_POR_ACCION[accion]
        else:
            operacion = VER if request.method in ("GET", "HEAD", "OPTIONS") else CREAR
        return puede(request.user, modulo, operacion)
