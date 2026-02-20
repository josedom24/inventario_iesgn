#!/usr/bin/env python3
"""
Script para generar PDF con 16 pegatinas (2 columnas x 8 filas), sin márgenes.
Dibuja directamente en el canvas para evitar problemas de paginación.
Uso: python3 test_pdf.py inventario_hw_min.csv reporte.pdf
"""

import csv
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

PAGE_WIDTH, PAGE_HEIGHT = A4   # ~595.27 x 841.89 puntos

COLS = 2
ROWS = 8
REGISTROS_POR_PAGINA = COLS * ROWS  # 16

CELL_W = PAGE_WIDTH  / COLS
CELL_H = PAGE_HEIGHT / ROWS


def crear_parrafo(registro):
    """Devuelve un Paragraph con los datos del registro."""
    codigo     = registro.get('codigo', 'N/A')
    cpu        = registro.get('cpu_model', 'N/A')
    ram        = registro.get('ram_gib', 'N/A')
    discos     = registro.get('discos', 'N/A')

    cpu_short    = cpu.split('@')[0].strip() if '@' in cpu else cpu
    cpu_short    = cpu_short[:45]
    discos_short = discos[:50]

    html = (
        f'<font size="14" face="Helvetica-Bold">{codigo}</font><br/><br/>'
        f'<font size="10"><b>CPU:</b> {cpu_short}</font><br/><br/>'
        f'<font size="10"><b>RAM:</b> {ram} GiB</font><br/><br/>'
        f'<font size="10"><b>Discos:</b> {discos_short}</font>'
    )

    style = ParagraphStyle(
        'Label',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=8,
        leading=10,
        spaceAfter=0,
    )
    return Paragraph(html, style)


def dibujar_pagina(c, registros_pagina):
    """Dibuja hasta 16 pegatinas en la página actual del canvas."""
    padding = 15  # puntos de margen interno en cada celda

    for idx, reg in enumerate(registros_pagina):
        col = idx % COLS
        row = idx // COLS

        # Coordenadas de la celda (origen ReportLab = esquina inferior-izquierda)
        x = col * CELL_W
        y = PAGE_HEIGHT - (row + 1) * CELL_H   # bajamos fila a fila

        # Líneas de corte opcionales (quitar si la hoja ya las trae)
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.3)
        c.rect(x, y, CELL_W, CELL_H)

        # Dibujar el contenido usando un Frame temporal
        parrafo = crear_parrafo(reg)
        frame = Frame(
            x + padding,
            y + padding,
            CELL_W - 2 * padding,
            CELL_H - 2 * padding,
            leftPadding=0, rightPadding=0,
            topPadding=0,  bottomPadding=0,
            showBoundary=0,
        )
        frame.addFromList([parrafo], c)


def generar_pdf(csv_path, pdf_output):
    print(f"[*] Leyendo CSV: {csv_path}")

    datos = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                datos.append(row)
    except FileNotFoundError:
        print(f"[!] Error: Archivo '{csv_path}' no encontrado")
        sys.exit(1)

    if not datos:
        print("[!] Error: El archivo CSV está vacío")
        sys.exit(1)

    print(f"[+] {len(datos)} registros encontrados")
    print(f"[*] Generando PDF: {pdf_output}")

    c = canvas.Canvas(pdf_output, pagesize=A4)

    for pagina_num in range(0, len(datos), REGISTROS_POR_PAGINA):
        registros_pagina = datos[pagina_num:pagina_num + REGISTROS_POR_PAGINA]
        dibujar_pagina(c, registros_pagina)
        c.showPage()   # nueva página (o cierra la última)

    c.save()

    total_paginas = (len(datos) + REGISTROS_POR_PAGINA - 1) // REGISTROS_POR_PAGINA
    print(f"[+] PDF generado: {pdf_output}")
    print(f"[+] Páginas: {total_paginas}  |  "
          f"Pegatina: {CELL_W/28.35:.1f}cm x {CELL_H/28.35:.1f}cm")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python3 test_pdf.py <archivo_csv> <archivo_pdf_salida>")
        sys.exit(1)

    generar_pdf(sys.argv[1], sys.argv[2])
