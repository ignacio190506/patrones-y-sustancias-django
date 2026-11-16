"""Archivos descargables de los reportes: PDF con ReportLab y Excel con openpyxl."""
from io import BytesIO
from xml.sax.saxutils import escape

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle

MARGEN = 28


def generar_pdf(titulo, columnas, filas_texto, secciones, seleccion=""):
    """Devuelve un PDF en memoria con el título, la tabla y las explicaciones del reporte."""
    buffer = BytesIO()
    pagina = landscape(A4)
    documento = SimpleDocTemplate(buffer, pagesize=pagina, title=titulo, leftMargin=MARGEN,
                                  rightMargin=MARGEN, topMargin=MARGEN, bottomMargin=MARGEN)
    estilos = getSampleStyleSheet()
    celda = ParagraphStyle("Celda", fontName="Helvetica", fontSize=9, leading=12)
    encabezado = ParagraphStyle("Encabezado", parent=celda, fontName="Helvetica-Bold")

    tabla = [[Paragraph(escape(columna), encabezado) for columna in columnas]]
    for fila in filas_texto:
        tabla.append([Paragraph(escape(valor), celda) for valor in fila])
    formato = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if not filas_texto:
        tabla.append([Paragraph("No hay datos para la selección.", celda)] + [""] * (len(columnas) - 1))
        formato.append(("SPAN", (0, 1), (-1, 1)))
    # Todas las columnas comparten el ancho útil de la página
    ancho_columna = (pagina[0] - 2 * MARGEN) / len(columnas)
    tabla_pdf = LongTable(tabla, colWidths=[ancho_columna] * len(columnas), repeatRows=1)
    tabla_pdf.setStyle(TableStyle(formato))

    elementos = [Paragraph(escape(titulo), estilos["Title"])]
    if seleccion:
        elementos.append(Paragraph("Filtros aplicados: " + escape(seleccion), estilos["Normal"]))
    elementos += [Spacer(1, 10), tabla_pdf]
    for subtitulo, parrafos in secciones:
        elementos.append(Paragraph(escape(subtitulo), estilos["Heading3"]))
        for parrafo in parrafos:
            elementos.append(Paragraph(escape(parrafo), estilos["Normal"]))
            elementos.append(Spacer(1, 4))
    documento.build(elementos)
    buffer.seek(0)
    return buffer


def generar_excel(nombre_hoja, columnas, filas):
    """Devuelve un .xlsx en memoria. Los números se guardan como números, no como texto."""
    libro = Workbook()
    hoja = libro.active
    hoja.title = nombre_hoja
    hoja.append(columnas)
    for fila in filas:
        hoja.append(fila)

    borde = Side(style="thin", color="D9D9D9")
    for fila in hoja:
        for celda in fila:
            celda.border = Border(left=borde, right=borde, top=borde, bottom=borde)
            if isinstance(celda.value, float):
                celda.number_format = "0.0"
    for celda in hoja[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="1F4E78")
        celda.alignment = Alignment(wrap_text=True, vertical="center")
    for numero in range(1, len(columnas) + 1):
        hoja.column_dimensions[get_column_letter(numero)].width = 24
    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions

    buffer = BytesIO()
    libro.save(buffer)
    buffer.seek(0)
    return buffer
