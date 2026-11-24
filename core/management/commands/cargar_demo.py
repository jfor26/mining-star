"""python manage.py cargar_demo --clave "UnaClaveSegura2026*"

Carga datos de demostracion para presentar el aplicativo:

- un usuario por cada cargo (gerente, admin.ms, supervisor, comercial,
  contador, operario, auxiliar), todos con la clave indicada;
- clientes, proveedores y productos del portafolio (rajon, caliza, cal
  agricola, marmolina, recebo, agregados);
- seis meses de ventas, dos semanas de produccion, oportunidades del CRM,
  pedidos, el repositorio normativo y acciones de mejora continua.

Es idempotente: si se ejecuta dos veces no duplica registros (busca por
documento, codigo o nombre). Los datos transaccionales solo se generan si la
base tiene menos de 5 ventas, salvo que se use --forzar.

IMPORTANTE: los nombres de clientes y proveedores son ficticios y los precios
son de demostracion. No usar en produccion.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import (
    AccionMejora,
    Cliente,
    Empleado,
    Interaccion,
    Oportunidad,
    Producto,
    Proveedor,
    RegistroProduccion,
    RequisitoNormativo,
    Venta,
)
from core.servicios import confirmar_pago, crear_pedido, registrar_venta

EMPLEADOS = [
    # usuario, documento, nombres, apellidos, cargo, area
    ("gerente", "1110000001", "Laura", "Restrepo", "Gerente", "Gerencia"),
    ("admin.ms", "1110000002", "Andrés", "Rojas", "Administrador", "Gerencia"),
    ("supervisor", "1110000003", "Carlos", "Molina", "Supervisor", "Operaciones"),
    ("comercial", "1110000004", "Diana", "Pardo", "Comercial", "Comercial"),
    ("contador", "1110000005", "Jorge", "Castro", "Contador", "Finanzas"),
    ("operario", "1110000006", "Luis", "Guzmán", "Operario", "Operaciones"),
    ("auxiliar", "1110000007", "Paula", "Rincón", "Auxiliar", "Logística"),
    (None, "1110000008", "Marta", "Lozano", "Supervisor", "Gestión Ambiental"),
    (None, "1110000009", "Óscar", "Vargas", "Operario", "Operaciones"),
]

# Dias de antiguedad de cada empleado de demostracion, para que el orden por
# tiempo laborado del modulo Empleados muestre diferencias reales.
ANTIGUEDAD_DIAS = {
    "1110000001": 2900, "1110000002": 1500, "1110000003": 2300, "1110000004": 700,
    "1110000005": 1100, "1110000006": 950, "1110000007": 120, "1110000008": 400,
    "1110000009": 45,
}

PROVEEDORES = [
    ("901000001", "Trituradora Andina S.A.S.", "Mario Pérez", "Ibagué"),
    ("901000002", "Empaques del Tolima Ltda.", "Sandra Díaz", "Espinal"),
    ("901000003", "Transportes La Resaca S.A.S.", "Hernán Ruiz", "San Luis"),
]

# codigo, nombre, categoria, proveedor(indice), compra, venta, stock, minimo
PRODUCTOS = [
    ("RAJ-001", "Rajón de caliza (tonelada)", "Material de cantera", 2, "15000", "24000", 900, 150),
    ("CAL-001", "Caliza para cemento (tonelada)", "Caliza industrial", 2, "17000", "32000", 600, 100),
    ("CAL-002", "Cal agrícola molida (bulto 50 kg)", "Cal agrícola", 1, "9000", "18500", 350, 60),
    ("MAR-001", "Marmolina blanca (bulto 40 kg)", "Marmolina", 1, "11000", "22000", 220, 40),
    ("AGR-001", "Agregado triturado 3/4\" (m³)", "Agregados", 0, "38000", "65000", 180, 50),
    ("REC-001", "Recebo para vías (m³)", "Agregados", 2, "18000", "30000", 40, 60),
    ("MAR-002", "Mármol travertino para enchape (m²)", "Mármol ornamental", 0, "55000", "98000", 12, 15),
]

CLIENTES = [
    ("900500001", "Constructora Vías del Centro S.A.S.", "compras@viasdelcentro.example", "Obra civil y vías"),
    ("900500002", "Concretos y Prefabricados del Llano S.A.S.", "suministros@concretosllano.example", "Concreteras"),
    ("900500003", "Agroinsumos El Arrozal S.A.S.", "pedidos@elarrozal.example", "Distribuidor agrícola"),
    ("900500004", "Marmolería Arte en Piedra", "ventas@arteenpiedra.example", "Marmolería"),
    ("900500005", "Consorcio Vial San Luis 2026", "obra@consorciosanluis.example", "Obra pública"),
    ("1105123456", "Ferretería La Paloma", "laferreteria@correo.example", "Ferretería"),
]

REQUISITOS = [
    # autoridad, categoria, nombre, norma, descripcion, periodicidad, dias_vence, estado
    ("ANM", "Minero", "Póliza minero-ambiental vigente",
     "Ley 685 de 2001 (Código de Minas), art. 280",
     "Garantiza el cumplimiento de las obligaciones mineras y ambientales del título. Debe mantenerse vigente y cargarse en AnnA Minería.",
     "Anual", 45, "EnTramite"),
    ("ANM", "Minero", "Formato Básico Minero (FBM)",
     "Ley 685 de 2001; reglamentación de la ANM",
     "Reporte de producción, inversiones, personal y aspectos técnicos de la operación, radicado en AnnA Minería.",
     "Anual", 20, "Pendiente"),
    ("ANM", "Minero", "Declaración y pago de regalías",
     "Ley 2056 de 2020 (Sistema General de Regalías); Ley 685 de 2001, art. 227",
     "Liquidación sobre el precio base de boca de mina fijado por la UPME. Se declara aun cuando la producción sea cero.",
     "Trimestral", 12, "Pendiente"),
    ("ANM", "Minero", "Inscripción y actualización en el RUCOM",
     "Registro Único de Comercializadores de Minerales – ANM",
     "Habilita la comercialización legal del mineral: los compradores exigen el certificado de origen y el RUCOM vigente.",
     "Anual", 70, "EnTramite"),
    ("ANM", "Minero", "Informe de recursos y reservas (estándar ECRR / CRIRSCO)",
     "Resolución ANM 100 de 2020",
     "Actualización de recursos y reservas con estándar internacional, firmada por persona competente.",
     "Única / al actualizar el PTO", 160, "Pendiente"),
    ("ANM", "Minero", "Plan de Gestión Social (PGS)",
     "Plan de Gestión Social – ANM",
     "Programas de relacionamiento y beneficio con la comunidad del área de influencia (Payandé).",
     "Anual", 110, "Pendiente"),
    ("CORTOLIMA", "Ambiental", "Licencia ambiental y Plan de Manejo Ambiental",
     "Decreto 1076 de 2015 (Único Reglamentario del Sector Ambiente)",
     "Cumplimiento de las fichas del PMA de la licencia ambiental otorgada por la autoridad ambiental regional.",
     "Permanente", None, "Cumplido"),
    ("CORTOLIMA", "Ambiental", "Informe de cumplimiento ambiental (ICA)",
     "Decreto 1076 de 2015",
     "Reporte periódico del avance de las medidas del Plan de Manejo Ambiental, con evidencias.",
     "Según acto administrativo", -5, "Vencido"),
    ("CORTOLIMA", "Ambiental", "Permiso de emisiones atmosféricas",
     "Decreto 1076 de 2015",
     "Requerido para fuentes de material particulado (trituración, vías internas, voladura).",
     "Según vigencia del permiso", 200, "EnTramite"),
    ("CORTOLIMA", "Ambiental", "Concesión de aguas y permiso de vertimientos (si aplica)",
     "Decreto 1076 de 2015",
     "Uso de agua para humectación de vías y control de polvo; manejo de aguas residuales del campamento.",
     "Según vigencia del permiso", None, "Pendiente"),
    ("MinTrabajo", "SST", "Sistema de Gestión de Seguridad y Salud en el Trabajo",
     "Decreto 1072 de 2015; Resolución 0312 de 2019",
     "Autoevaluación de estándares mínimos, plan anual de trabajo y reporte de indicadores.",
     "Anual", 85, "EnTramite"),
    ("MinEnergia", "SST", "Reglamento de seguridad en labores mineras a cielo abierto",
     "Decreto 2222 de 1993",
     "Condiciones de higiene y seguridad en la explotación a cielo abierto: taludes, voladuras, maquinaria y señalización.",
     "Permanente", None, "Cumplido"),
    ("MinEnergia", "Minero", "Permiso para uso de explosivos",
     "Decreto 2535 de 1993",
     "Autorización para adquisición, transporte, almacenamiento (polvorín) y uso de explosivos en voladuras.",
     "Por consumo", 30, "Pendiente"),
    ("SIC", "Datos", "Política de tratamiento de datos personales",
     "Ley 1581 de 2012; Decreto 1377 de 2013",
     "Autorización de los titulares y política publicada para los datos de clientes y empleados que guarda Mining Star ERP.",
     "Permanente", None, "Cumplido"),
    ("DIAN", "Tributario", "Facturación electrónica de ventas",
     "Estatuto Tributario, art. 616-1",
     "Cada venta de mineral debe soportarse con factura electrónica validada por la DIAN.",
     "Por operación", None, "Cumplido"),
]

ACCIONES = [
    ("Polvo en la vía interna afecta a vecinos", "Ambiental", "Correctiva",
     "Queja de la comunidad por material particulado en temporada seca.",
     "No hay programa de humectación de vías.", "Humectar la vía dos veces al día y medir con monitoreo de PM10.",
     "Hacer"),
    ("Retraso en el reporte de producción por turno", "Indicador", "Mejora",
     "El 30 % de los turnos se registran al día siguiente.", "El registro se hacía en papel.",
     "Registrar la producción en el aplicativo desde el celular al cerrar el turno.", "Verificar"),
    ("Casi accidente en zona de cargue", "SST", "Preventiva",
     "Volqueta retrocedió sin señalero.", "No existía procedimiento de cargue.",
     "Procedimiento de cargue con señalero y capacitación a conductores.", "Planear"),
    ("Clientes piden certificado de origen con la factura", "Cliente", "Mejora",
     "Dos clientes de obra pública solicitaron certificado de origen en cada despacho.", "",
     "Generar el certificado desde el módulo de ventas.", "Planear"),
    ("Inventario de cal agrícola descuadrado", "Auditoria", "Correctiva",
     "Diferencia de 12 bultos entre el sistema y la bodega.", "Despachos sin registro de venta.",
     "Todo despacho debe salir con venta registrada en el sistema.", "Cerrada"),
]


class Command(BaseCommand):
    help = "Carga datos de demostracion y un usuario por cargo."

    def add_arguments(self, parser):
        parser.add_argument("--clave", required=True,
                            help="Clave para los usuarios de demostracion (debe ser segura).")
        parser.add_argument("--forzar", action="store_true",
                            help="Genera ventas y produccion aunque ya existan datos.")
        parser.add_argument("--semilla", type=int, default=2026)

    @transaction.atomic
    def handle(self, *args, **op):
        try:
            validate_password(op["clave"])
        except ValidationError as error:
            raise CommandError("Clave insegura: " + " ".join(error.messages)) from error
        azar = random.Random(op["semilla"])
        hoy = timezone.localdate()

        empleados = {}
        for usuario, doc, nombres, apellidos, cargo, area in EMPLEADOS:
            emp, _ = Empleado.objects.get_or_create(documento=doc, defaults={
                "nombres": nombres, "apellidos": apellidos, "cargo": cargo, "area": area,
                "correo": f"{(usuario or nombres).lower().replace('.', '')}@miningstar.example",
                "telefono": "3000000000", "fecha_ingreso": hoy - timedelta(days=ANTIGUEDAD_DIAS.get(doc, 400)),
            })
            # Los nombres de la demo pueden cambiar entre versiones: se actualizan.
            if (emp.nombres, emp.apellidos) != (nombres, apellidos):
                emp.nombres, emp.apellidos = nombres, apellidos
                emp.save(update_fields=["nombres", "apellidos"])
            empleados[doc] = emp
            if usuario:
                user, creado = User.objects.get_or_create(username=usuario, defaults={
                    "first_name": nombres, "last_name": apellidos, "email": emp.correo,
                })
                user.first_name, user.last_name = nombres, apellidos
                user.set_password(op["clave"])
                user.is_staff = cargo == "Administrador"
                user.save()
                user.groups.set([Group.objects.get_or_create(name=cargo)[0]])
                if emp.usuario_id is None:
                    emp.usuario = user
                    emp.save(update_fields=["usuario"])
        self.stdout.write(f"Empleados: {Empleado.objects.count()} | usuarios demo listos")

        proveedores = []
        for nit, empresa, contacto, ciudad in PROVEEDORES:
            p, _ = Proveedor.objects.get_or_create(nit=nit, defaults={
                "empresa": empresa, "contacto": contacto, "ciudad": ciudad,
                "correo": f"contacto{nit[-1]}@proveedor.example", "telefono": "3100000000",
                "direccion": "Zona industrial",
            })
            proveedores.append(p)

        productos = []
        for codigo, nombre, cat, iprov, compra, venta, stock, minimo in PRODUCTOS:
            p, _ = Producto.objects.get_or_create(codigo=codigo, defaults={
                "nombre": nombre, "categoria": cat, "proveedor": proveedores[iprov],
                "precio_compra": Decimal(compra), "precio_venta": Decimal(venta),
                "stock": stock, "stock_minimo": minimo,
            })
            productos.append(p)

        clientes = []
        for doc, nombre, correo, segmento in CLIENTES:
            c, _ = Cliente.objects.get_or_create(documento=doc, defaults={
                "nombre": nombre, "correo": correo, "telefono": "3200000000", "empresa": segmento,
            })
            clientes.append(c)

        for autoridad, cat, nombre, norma, desc, periodo, dias, estado in REQUISITOS:
            RequisitoNormativo.objects.get_or_create(nombre=nombre, defaults={
                "autoridad": autoridad, "categoria": cat, "norma": norma, "descripcion": desc,
                "periodicidad": periodo, "estado": estado,
                "fecha_vencimiento": hoy + timedelta(days=dias) if dias is not None else None,
                "responsable": empleados["1110000008"] if cat == "Ambiental" else empleados["1110000001"],
            })

        admin = User.objects.get(username="admin.ms")
        for titulo, origen, tipo, desc, causa, plan, fase in ACCIONES:
            AccionMejora.objects.get_or_create(titulo=titulo, defaults={
                "origen": origen, "tipo": tipo, "descripcion": desc, "causa_raiz": causa,
                "plan_accion": plan, "fase": fase, "responsable": empleados["1110000003"],
                "fecha_compromiso": hoy + timedelta(days=azar.randint(5, 40)),
                "resultado": "Conteo de cierre de mes sin diferencias." if fase == "Cerrada" else "",
                "creado_por": admin,
            })

        if Venta.objects.count() >= 5 and not op["forzar"]:
            self.stdout.write(self.style.WARNING(
                "Ya hay ventas registradas: no se generan datos transaccionales (use --forzar)."))
        else:
            self._transacciones(azar, hoy, clientes, productos, empleados)

        self.stdout.write(self.style.SUCCESS(
            "Datos de demostracion cargados. Usuarios: "
            + ", ".join(u for u, *_ in EMPLEADOS if u)
        ))

    def _transacciones(self, azar, hoy, clientes, productos, empleados):
        comercial = empleados["1110000004"]
        vendibles = [p for p in productos if p.stock > 100]
        # Ventas de los ultimos seis meses, con tendencia creciente.
        for dias_atras in range(175, -1, -4):
            for _ in range(1 + (175 - dias_atras) // 60):
                producto = azar.choice(vendibles)
                producto.refresh_from_db()
                cantidad = azar.randint(3, 25)
                if producto.stock - cantidad < producto.stock_minimo:
                    continue
                venta = registrar_venta(azar.choice(clientes), producto, cantidad, comercial)
                momento = timezone.now() - timedelta(days=dias_atras, hours=azar.randint(0, 8))
                Venta.objects.filter(pk=venta.pk).update(fecha=momento)

        supervisor = empleados["1110000003"]
        operario = User.objects.get(username="operario")
        for dias_atras in range(13, -1, -1):
            fecha = hoy - timedelta(days=dias_atras)
            for turno in ("Manana", "Tarde"):
                for material, base in (("Caliza", 38), ("Marmol", 14), ("Recebo", 22)):
                    RegistroProduccion.objects.get_or_create(
                        fecha=fecha, turno=turno, material=material,
                        defaults={"cantidad": Decimal(base + azar.randint(-6, 9)), "unidad": "t",
                                  "supervisor": supervisor, "registrado_por": operario},
                    )

        etapas = ["Prospecto", "Contactado", "Cotizacion", "Negociacion", "Ganada", "Perdida", "Cotizacion"]
        titulos = ["Suministro de rajón para vía terciaria", "Caliza para planta de concreto",
                   "Cal agrícola temporada de siembra", "Marmolina para pisos", "Recebo mantenimiento vial",
                   "Agregado para prefabricados", "Enchape travertino lobby"]
        for i, (titulo, etapa) in enumerate(zip(titulos, etapas, strict=True)):
            cliente = clientes[i % len(clientes)]
            oportunidad, creada = Oportunidad.objects.get_or_create(titulo=titulo, defaults={
                "cliente": cliente, "etapa": etapa, "responsable": comercial,
                "valor_estimado": Decimal(azar.randint(8, 120) * 1_000_000),
                "fecha_cierre_estimada": hoy + timedelta(days=azar.randint(10, 90)),
            })
            if creada:
                Interaccion.objects.create(
                    cliente=cliente, oportunidad=oportunidad, tipo=azar.choice(["Llamada", "Visita", "Correo"]),
                    descripcion=f"Seguimiento: {titulo.lower()}.", proxima_accion="Enviar cotización actualizada",
                    fecha=timezone.now() - timedelta(days=azar.randint(1, 20)),
                )

        # Un pedido pagado (simulado) y uno pendiente, para la tienda.
        pagado = crear_pedido(clientes[2], [(productos[2], 10), (productos[3], 5)])
        confirmar_pago(pagado, "simulado", "SIM-DEMO-1")
        crear_pedido(clientes[3], [(productos[3], 4)])
        self.stdout.write(f"Ventas: {Venta.objects.count()} | Producción: {RegistroProduccion.objects.count()}")
