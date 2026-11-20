#!/usr/bin/env python3
"""
Convierte un notebook Jupyter (.ipynb) a PDF y lo guarda en docs/.

Uso:
    python scripts/notebook_a_pdf.py ruta/al/notebook.ipynb
    python scripts/notebook_a_pdf.py "notebooks/unidad_ii_exploracion/02_Limpieza de datos.ipynb"

Intenta varios métodos en orden:
1. nbconvert + weasyprint (si está instalado con GTK)
2. nbconvert + pdfkit/wkhtmltopdf (si wkhtmltopdf está instalado)
3. nbconvert --to pdf via LaTeX (si hay distribución LaTeX)
4. Guarda HTML y da instrucciones para imprimir a PDF manualmente

Requisitos mínimos:
    pip install nbconvert
Opcionales (para PDF automático):
    pip install weasyprint     # requiere GTK en Windows
    pip install pdfkit         # requiere wkhtmltopdf instalado
    # O instalar MiKTeX/TeX Live para nbconvert --to pdf
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def run_cmd(cmd, description):
    """Ejecuta comando y retorna (exito, output)."""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, f"Comando no encontrado: {cmd[0]}"


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/notebook_a_pdf.py <ruta_al_notebook.ipynb>")
        sys.exit(1)

    notebook_path = Path(sys.argv[1])

    if not notebook_path.exists():
        print(f"Error: No existe el archivo: {notebook_path}")
        sys.exit(1)

    if notebook_path.suffix != ".ipynb":
        print("Error: El archivo debe tener extension .ipynb")
        sys.exit(1)

    # Carpeta de salida: docs/ en la raiz del proyecto
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_name = notebook_path.stem + ".pdf"
    output_path = output_dir / pdf_name

    print(f"Convirtiendo: {notebook_path}")
    print(f"Salida: {output_path}")

    # Paso 1: Siempre generar HTML primero (nbconvert HTML es robusto)
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_html:
        html_path = Path(tmp_html.name)

    try:
        cmd_html = [
            sys.executable, "-m", "nbconvert",
            "--to", "html",
            "--output", str(html_path.with_suffix("")),
            str(notebook_path),
        ]
        success, out = run_cmd(cmd_html, "nbconvert a HTML")
        if not success:
            print(f"Error generando HTML: {out}")
            sys.exit(1)
        print("  [OK] HTML generado")

        # Método 1: weasyprint
        try:
            from weasyprint import HTML
            HTML(html_path).write_pdf(output_path)
            print(f"  [OK] PDF generado con weasyprint: {output_path}")
            return
        except Exception as e:
            print(f"  [INFO] weasyprint no disponible: {e}")

        # Método 2: pdfkit (wkhtmltopdf)
        try:
            import pdfkit
            pdfkit.from_file(str(html_path), str(output_path))
            print(f"  [OK] PDF generado con pdfkit/wkhtmltopdf: {output_path}")
            return
        except Exception as e:
            print(f"  [INFO] pdfkit/wkhtmltopdf no disponible: {e}")

        # Método 3: nbconvert --to pdf (LaTeX)
        success, out = run_cmd([
            sys.executable, "-m", "nbconvert",
            "--to", "pdf",
            "--output", str(output_path.with_suffix("")),
            str(notebook_path),
        ], "nbconvert a PDF (LaTeX)")
        if success:
            print(f"  [OK] PDF generado con LaTeX: {output_path}")
            return
        else:
            print(f"  [INFO] LaTeX no disponible: {out}")

        # Método 4: Guardar HTML y dar instrucciones
        html_final = output_dir / (notebook_path.stem + ".html")
        shutil.copy2(html_path, html_final)
        print(f"\n  [AVISO] No se pudo generar PDF automaticamente.")
        print(f"  Se guardo el HTML en: {html_final}")
        print(f"  Para obtener el PDF:")
        print(f"    1. Abre el archivo HTML en tu navegador")
        print(f"    2. Imprime (Ctrl+P) -> 'Guardar como PDF'")
        print(f"    3. Guarda en: {output_path}")

    finally:
        # Limpiar HTML temporal
        if html_path.exists():
            html_path.unlink()


if __name__ == "__main__":
    main()