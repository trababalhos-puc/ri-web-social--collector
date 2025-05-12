import os
import subprocess
import tempfile
import shutil
import requests


def pdf_to_html_string(pdf_source):
    """
    Converte um PDF (arquivo local ou URL) para HTML e retorna como string.

    Parâmetros:
    -----------
    pdf_source : str
        Caminho para o arquivo PDF local ou URL para um PDF online

    Retorna:
    --------
    str
        Conteúdo HTML como uma string
    """
    temp_dir = tempfile.mkdtemp()

    try:
        if pdf_source.startswith("http://") or pdf_source.startswith("https://"):
            temp_pdf = os.path.join(temp_dir, "temp_file.pdf")
            response = requests.get(pdf_source, stream=True, timeout=30)
            response.raise_for_status()

            with open(temp_pdf, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            pdf_path = temp_pdf
        else:
            pdf_path = pdf_source
        temp_html_base = os.path.join(temp_dir, "temp_output")
        subprocess.run(
            ["pdftohtml", "-c", "-q", "-noframes", "-i", pdf_path, temp_html_base],
            check=True,
        )
        temp_html_file = temp_html_base + ".html"

        if not os.path.exists(temp_html_file):
            raise FileNotFoundError('pdftohtml falhou ao gerar o arquivo HTML')
        with open(temp_html_file, "r", encoding="utf-8", errors="replace") as f:
            html_content = f.read()
        enhanced_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Convertido</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            margin: 2em; 
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        table {{
            border-collapse: collapse;
            margin: 15px 0;
            width: auto;
        }}
        td, th {{
            border: 1px solid #ddd;
            padding: 8px;
        }}
        hr {{
            border: 0;
            height: 1px;
            background-color: #eee;
            margin: 30px 0;
        }}
        .pdf-page {{
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

        return enhanced_html

    except subprocess.CalledProcessError as e:
        try:
            subprocess.run(
                ["pdftohtml", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            raise Exception(
                "pdftohtml não encontrado. Instale o pacote poppler-utils."
            ) from e
        raise Exception(f"Erro ao executar pdftohtml: {e}") from e

    except Exception as e:
        raise Exception(f"Erro ao converter PDF para HTML: {e}") from e

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def convert_local_pdf(pdf_path):
    try:
        html_string = pdf_to_html_string(pdf_path)
        print(
            f"PDF convertido com sucesso! Tamanho do HTML: {len(html_string)} caracteres"
        )
        return html_string
    except Exception as e:
        print(f"Erro: {e}")
        return None


def convert_pdf_from_url(pdf_url):
    try:
        html_string = pdf_to_html_string(pdf_url)
        print(
            f"PDF da URL convertido com sucesso! Tamanho do HTML: {len(html_string)} caracteres"
        )
        return html_string
    except Exception as e:
        print(f"Erro: {e}")
        return None


def process_pdf_urls(urls):
    results = []
    for url in urls:
        try:
            html = pdf_to_html_string(url)
            results.append((url, html))
            print(f"Convertido: {url}")
        except Exception as e:
            results.append((url, None))
            print(f"Falha: {url} - {e}")
    return results


def convert_pdf(url):
    return convert_pdf_from_url(url)
