"""
Generadores de reportes Excel y PDF.

ANTES: cada modelo tenia su propia funcion de exportacion con el mismo
codigo copiado y pegado (8 funciones, ~1.900 lineas en total). Si querias
cambiar el color del encabezado tenias que editarlo en 8 sitios.

AHORA: se describe QUE columnas lleva el reporte y estas dos funciones se
encargan del COMO. Una sola implementacion, un solo sitio que mantener.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

# Identidad visual de los reportes, definida UNA vez.
AZUL_CORPORATIVO = "1F4E78"
GRIS_BORDE = "B7B7B7"
GRIS_FILA = "F3F6F9"
EMPRESA = "MINING STAR ERP"

MIME_EXCEL = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


@dataclass(frozen=True)
class Columna:
    """Describe una columna del reporte.

    encabezado: texto que aparece en la cabecera.
    valor:      funcion que extrae el dato de cada objeto.
    ancho:      ancho en puntos para el PDF.
    izquierda:  True para alinear el texto a la izquierda (nombres, correos).
    """

    encabezado: str
    valor: Callable[[Any], Any]
    ancho: int = 80
    izquierda: bool = False


def _nombre_archivo(base: str, extension: str) -> str:
    fecha = datetime.now().strftime("%d-%m-%Y")
    return f"{base}_{fecha}.{extension}"


# =========================================================
# EXCEL
# =========================================================

def exportar_excel(
    filas: Iterable[Any],
    columnas: list[Columna],
    titulo_hoja: str,
    nombre_base: str,
) -> HttpResponse:
    """Construye un .xlsx con encabezado con estilo y anchos automaticos."""

    libro = Workbook()
    hoja = libro.active
    hoja.title = titulo_hoja

    relleno = PatternFill(
        start_color=AZUL_CORPORATIVO,
        end_color=AZUL_CORPORATIVO,
        fill_type="solid",
    )
    fuente = Font(color="FFFFFF", bold=True)
    centrado = Alignment(horizontal="center", vertical="center")

    # Encabezados
    for indice, columna in enumerate(columnas, start=1):
        celda = hoja.cell(row=1, column=indice, value=columna.encabezado)
        celda.fill = relleno
        celda.font = fuente
        celda.alignment = centrado

    # Datos
    for numero_fila, objeto in enumerate(filas, start=2):
        for indice, columna in enumerate(columnas, start=1):
            hoja.cell(row=numero_fila, column=indice, value=columna.valor(objeto))

    # Ancho de columna aproximado segun el encabezado
    for indice, columna in enumerate(columnas, start=1):
        hoja.column_dimensions[get_column_letter(indice)].width = max(
            14, len(columna.encabezado) + 4
        )

    # Congela la fila de encabezados al hacer scroll
    hoja.freeze_panes = "A2"

    respuesta = HttpResponse(content_type=MIME_EXCEL)
    respuesta["Content-Disposition"] = (
        f'attachment; filename="{_nombre_archivo(nombre_base, "xlsx")}"'
    )
    libro.save(respuesta)
    return respuesta


# =========================================================
# PDF
# =========================================================

def exportar_pdf(
    filas: Iterable[Any],
    columnas: list[Columna],
    titulo_reporte: str,
    nombre_base: str,
) -> HttpResponse:
    """Construye un .pdf apaisado con tabla, cabecera repetida y filas cebra."""

    respuesta = HttpResponse(content_type="application/pdf")
    respuesta["Content-Disposition"] = (
        f'attachment; filename="{_nombre_archivo(nombre_base, "pdf")}"'
    )

    documento = SimpleDocTemplate(
        respuesta,
        pagesize=letter,
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30,
        title=titulo_reporte,
        author=EMPRESA,
    )

    base = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloReporte",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor(f"#{AZUL_CORPORATIVO}"),
        spaceAfter=6,
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloReporte",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=15,
    )
    celda_centro = ParagraphStyle(
        "CeldaCentro",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
    )
    celda_izquierda = ParagraphStyle(
        "CeldaIzquierda",
        parent=celda_centro,
        alignment=TA_LEFT,
    )

    fecha_actual = datetime.now().strftime("%d-%m-%Y")

    elementos = [
        Paragraph(EMPRESA, estilo_titulo),
        Paragraph(titulo_reporte, estilo_subtitulo),
        Paragraph(f"Fecha de generacion: {fecha_actual}", estilo_subtitulo),
    ]

    # Cabecera de la tabla
    datos = [[
        Paragraph(f"<b>{columna.encabezado}</b>", celda_centro)
        for columna in columnas
    ]]

    # Cuerpo de la tabla
    for objeto in filas:
        datos.append([
            Paragraph(
                str(columna.valor(objeto) if columna.valor(objeto) is not None else ""),
                celda_izquierda if columna.izquierda else celda_centro,
            )
            for columna in columnas
        ])

    tabla = Table(
        datos,
        repeatRows=1,                                   # cabecera en cada pagina
        colWidths=[columna.ancho for columna in columnas],
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(f"#{AZUL_CORPORATIVO}")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(f"#{GRIS_BORDE}")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor(f"#{GRIS_FILA}")]),
    ]))

    elementos.append(tabla)
    documento.build(elementos)
    return respuesta
