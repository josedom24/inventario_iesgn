#!/usr/bin/env python3
"""
Script para generar PDF con 2 cuadros por fila, fondo blanco
Uso: python3 test_pdf.py inventario_hw_min.csv reporte.pdf
"""

import csv
import io
import sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors


def crear_celda_hardware(registro):
    """Crea el contenido de una celda con información del hardware"""
    codigo = registro.get('codigo', 'N/A')
    cpu = registro.get('cpu_model', 'N/A')
    ram = registro.get('ram_gib', 'N/A')
    discos = registro.get('discos', 'N/A')
    
    # Simplificar CPU
    cpu_short = cpu.split('@')[0].strip() if '@' in cpu else cpu
    cpu_short = cpu_short[:45] if len(cpu_short) > 45 else cpu_short
    
    # Simplificar discos
    discos_short = discos[:50] if len(discos) > 50 else discos
    
    html = f"""
    <font size="14" face="Helvetica-Bold">{codigo}</font><br/><br/><br/>
    <font size="10"><b>CPU:</b> {cpu_short}</font><br/><br/>
    <font size="10"><b>RAM:</b> {ram} GiB</font><br/><br/>
    <font size="10"><b>Discos:</b> {discos_short}</font>
    """
    
    styles = ParagraphStyle(
        'CustomStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=8,
        leading=8,
        alignment=0,
        spaceAfter=0
    )
    
    return Paragraph(html, styles)


def generar_pdf(csv_path, pdf_output):
    """Genera un PDF a partir de un CSV con 2 columnas por fila"""
    
    print(f"[*] Leyendo CSV: {csv_path}")
    
    # Leer datos del CSV
    datos = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                datos.append(row)
    except FileNotFoundError:
        print(f"[!] Error: Archivo '{csv_path}' no encontrado")
        sys.exit(1)
    
    if not datos:
        print("[!] Error: El archivo CSV está vacío")
        sys.exit(1)
    
    print(f"[+] Se encontraron {len(datos)} registros")
    
    # Crear PDF
    print(f"[*] Generando PDF: {pdf_output}")
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=0.3*cm,
        leftMargin=0.3*cm,
        topMargin=0.3*cm,
        bottomMargin=0.3*cm
    )
    
    story = []
    registros_por_pagina = 16  # 8 filas x 2 columnas
    
    for pagina_num in range(0, len(datos), registros_por_pagina):
        if pagina_num > 0:
            story.append(PageBreak())
        
        registros_pagina = datos[pagina_num:pagina_num + registros_por_pagina]
        tabla_data = []
        
        # Crear filas de 2 celdas (sin filas espaciadoras porque no hay bordes)
        num_filas_contenido = (len(registros_pagina) + 1) // 2
        
        for idx_fila_contenido in range(num_filas_contenido):
            fila_idx = idx_fila_contenido * 2
            
            # Fila de contenido
            fila = []
            
            # Primera columna
            if fila_idx < len(registros_pagina):
                fila.append(crear_celda_hardware(registros_pagina[fila_idx]))
            else:
                fila.append("")
            
            # Espaciador horizontal
            fila.append("")
            
            # Segunda columna
            if fila_idx + 1 < len(registros_pagina):
                fila.append(crear_celda_hardware(registros_pagina[fila_idx + 1]))
            else:
                fila.append("")
            
            tabla_data.append(fila)
        
        # Crear tabla con rowHeights uniforme
        tabla = Table(tabla_data, colWidths=[9.75*cm, 0.2*cm, 9.75*cm], rowHeights=[2.8*cm] * len(tabla_data))
        
        # Preparar estilos (sin bordes)
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]
        
        tabla.setStyle(TableStyle(style_commands))
        
        story.append(tabla)
    
    # Generar PDF
    doc.build(story)
    
    # Guardar PDF
    with open(pdf_output, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    total_paginas = (len(datos) + 15) // 16
    print(f"[+] PDF generado correctamente: {pdf_output}")
    print(f"[+] Total páginas: {total_paginas}")
    print(f"[+] Registros por página: 16 (8 filas x 2 columnas)")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python3 test_pdf.py <archivo_csv> <archivo_pdf_salida>")
        print("")
        print("Ejemplo:")
        print("  python3 test_pdf.py inventario_hw_min.csv reporte.pdf")
        sys.exit(1)
    
    csv_input = sys.argv[1]
    pdf_output = sys.argv[2]
    
    generar_pdf(csv_input, pdf_output)
