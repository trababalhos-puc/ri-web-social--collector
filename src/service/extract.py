import os
import re
import time
import unicodedata
from datetime import datetime
import concurrent.futures


import boto3
import chardet
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from service.convert import convert_pdf
from config import drive



class IPEAExtractor:
    def __init__(
        self,
        javascript_command,
        bucket_name=None,
        s3_key_prefix="ipeadata",
        headless: bool = False,
    ):
        self.url = "http://www.ipeadata.gov.br/Default.aspx"
        self.javascript_command = javascript_command
        self.bucket_name = bucket_name
        self.s3_key_prefix = s3_key_prefix
        self.driver = drive.DriverManager().start_driver(headless=False)
        self.s3 = boto3.client("s3") if bucket_name else None

    @staticmethod
    def __sanitize_filename(input_string):
        normalized = unicodedata.normalize("NFKD", input_string)
        ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
        sanitized = re.sub(r"[^\w\-_\.=]", "_", ascii_only)
        sanitized = re.sub(r"_+", "_", sanitized)
        return sanitized.strip("_")

    @staticmethod
    def __convert_to_utf8(html_content):
        result = chardet.detect(
            html_content if isinstance(html_content, bytes) else html_content.encode()
        )
        original_encoding = result["encoding"]
        try:
            decoded = (
                html_content.decode(original_encoding)
                if isinstance(html_content, bytes)
                else html_content
            )
            return decoded.encode("utf-8")
        except Exception:
            return html_content.encode("utf-8", errors="ignore")

    @staticmethod
    def __convert_date(date):
        data_extract = date.split("-")[1].strip()
        data_extract = data_extract.rstrip("T")
        if "/" in data_extract:
            date_obj = datetime.strptime(data_extract, "%d/%m/%Y")
        elif "." in data_extract:
            date_obj = datetime.strptime(data_extract, "%Y.%m")
        elif len(data_extract) == 4:
            year = int(data_extract)
            date_obj = datetime(year, 12, 31)
        else:
            print(data_extract)
            raise ValueError("Formato de data desconhecido.")

        return date_obj.strftime("%Y-%m-%d")

    def run_extraction(self):
        self.driver.get(self.url)
        self.driver.execute_script(f"javascript:{self.javascript_command}")

        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        self.driver.switch_to.frame(iframe)

        table = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "grid_DXMainTable"))
        )

        dados = []
        max_attempts = 3

        for i in range(1, len(table.find_elements(By.TAG_NAME, "tr"))):
            attempts = 0
            while attempts < max_attempts:
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    cells = rows[i].find_elements(By.TAG_NAME, "td")
                    if not cells:
                        break
                    try:
                        link_element = cells[1].find_element(By.TAG_NAME, "a")
                        href = link_element.get_attribute("href")
                        nome = link_element.text
                    except Exception:
                        break
                    match = re.search(r"javascript:show\((\d+)\)", href)
                    numero_js = match.group(1) if match else ""
                    unidade = cells[2].text
                    freq = cells[3].text
                    periodo = cells[4].text
                    iso_date = self.__convert_date(periodo)
                    data = [numero_js, nome, unidade, freq, periodo, iso_date]
                    print(data)
                    html_utf8 = self.__extract_html(data)
                    self.extract_pdf_links(html_utf8)
                    self.driver.back()
                    time.sleep(1)
                    iframe = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                    )
                    self.driver.switch_to.frame(iframe)
                    table = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, "grid_DXMainTable"))
                    )
                    dados.append(data)
                    break
                except StaleElementReferenceException:
                    attempts += 1
                    if attempts == max_attempts:
                        print(
                            f"Failed to process row {i} after {max_attempts} attempts"
                        )
                        break
        self.driver.quit()
        return dados

    def __upload_to_s3(self, file_name, key, content):
        _key = f"{self.s3_key_prefix}/{key}/{file_name}".replace("//", "/")
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content

        if self.bucket_name:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=_key,
                Body=content_bytes,
                ContentType="text/html",
            )
            print(f"Arquivo salvo no S3 em: s3://{self.bucket_name}/{key}")
        else:
            folder = f"{self.s3_key_prefix}/{key}"
            os.makedirs(folder, exist_ok=True)
            with open(_key, "wb") as f:
                f.write(content_bytes)

    def __extract_html(self, data):
        numero_js = data[0]
        self.driver.execute_script(f"javascript:show({int(numero_js)})")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        folder_name = self.__sanitize_filename("==".join(data[1:4]))
        file_name = self.__sanitize_filename("_".join(data)) + ".html"
        html_utf8 = self.__convert_to_utf8(self.driver.page_source)
        self.__upload_to_s3(file_name, f"date={data[-1]}/{folder_name}", html_utf8)
        return html_utf8

    def extract_pdf_links(self, html_utf8):
        """
        Extrai todos os links de PDF que começam com '../doc' e terminam com '.pdf'
        do conteúdo HTML e os converte para URLs completas.

        Args:
            html_utf8 (bytes ou str): Conteúdo HTML para extrair os links.

        Returns:
            list: Lista de strings contendo as URLs completas dos PDFs encontrados.
        """
        # Converte para string se estiver em bytes
        if isinstance(html_utf8, bytes):
            html_utf8 = html_utf8.decode('utf-8')
        pattern = r'href=["\'](\.\.\/doc[^"\']*\.pdf)["\']'
        relative_pdf_links = re.findall(pattern, html_utf8)
        base_url = "http://www.ipeadata.gov.br"
        absolute_pdf_links = []

        for link in relative_pdf_links:
            absolute_link = link.replace('../', f'{base_url}/')
            absolute_pdf_links.append(absolute_link)
        if len(absolute_pdf_links):
            result = self.extract_pdfs_in_parallel(list(set(absolute_pdf_links)))
            for html_name in result:
                name = html_name.split('/doc/')[-1].replace(' ', '_').replace('.pdf', '.html')
                if result[html_name]:
                    content = result[html_name]
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    self.__upload_to_s3(name, f"pdf_to_html/date={datetime.now().date()}/", content)
        else:
            print('nao possui links para pdfs')

    @staticmethod
    def extract_pdfs_in_parallel(pdf_urls, max_workers=5):
        """
        Realiza a extração de múltiplos PDFs em paralelo.

        Args:
            pdf_urls (list): Lista de URLs de PDFs para processar.
            max_workers (int, opcional): Número máximo de workers para processamento paralelo.

        Returns:
            dict: Dicionário com as URLs como chaves e o conteúdo HTML como valores.
        """
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(convert_pdf, url): url for url in pdf_urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    html_content = future.result()
                    results[url] = html_content
                    print(f"Extraído com sucesso: {url}")
                except Exception as e:
                    print(f"Erro ao processar {url}: {str(e)}")
                    results[url] = None
        return results