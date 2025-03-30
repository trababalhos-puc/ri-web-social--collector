import re
import csv
import os
import boto3
import time
import unicodedata
import chardet
from datetime import datetime

from config import drive
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


class IPEAExtractor:
    def __init__(self, javascript_command, bucket_name=None, s3_key_prefix='ipeadata', headless: bool = False):
        self.url = 'http://www.ipeadata.gov.br/Default.aspx'
        self.javascript_command = javascript_command
        self.bucket_name = bucket_name
        self.s3_key_prefix = s3_key_prefix
        self.driver = drive.DriverManager().start_driver(headless=headless)
        self.s3 = boto3.client('s3') if bucket_name else None

    @staticmethod
    def __sanitize_filename(input_string):
        normalized = unicodedata.normalize('NFKD', input_string)
        ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
        sanitized = re.sub(r'[^\w\-_\.=]', '_', ascii_only)
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')

    @staticmethod
    def __convert_to_utf8(html_content):
        result = chardet.detect(html_content if isinstance(html_content, bytes) else html_content.encode())
        original_encoding = result['encoding']
        try:
            decoded = html_content.decode(original_encoding) if isinstance(html_content, bytes) else html_content
            return decoded.encode('utf-8')
        except:
            return html_content.encode('utf-8', errors='ignore')

    @staticmethod
    def __convert_date(date):
        data_extract = date.split('-')[1].strip()
        data_extract = data_extract.rstrip("T")
        if '/' in data_extract:
            date_obj = datetime.strptime(data_extract, "%d/%m/%Y")
        elif '.' in data_extract:
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

        for i in range(1, len(table.find_elements(By.TAG_NAME, 'tr'))):
            attempts = 0
            while attempts < max_attempts:
                try:
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    cells = rows[i].find_elements(By.TAG_NAME, 'td')
                    if not cells:
                        break
                    try:
                        link_element = cells[1].find_element(By.TAG_NAME, 'a')
                        href = link_element.get_attribute('href')
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
                    self.__extract_html(data)
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
                        print(f"Failed to process row {i} after {max_attempts} attempts")
                        break
        self.driver.quit()
        return dados


    def __upload_to_s3(self, file_name, key, content_bytes):
        _key = f"{self.s3_key_prefix}/{key}/{file_name}".replace('//', '/')
        if self.bucket_name:
            self.s3.put_object(Bucket=self.bucket_name, Key=_key, Body=content_bytes, ContentType='text/html')
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
        folder_name = self.__sanitize_filename('=='.join(data[1:4]))
        file_name = self.__sanitize_filename('_'.join(data)) + '.html'
        html_utf8 = self.__convert_to_utf8(self.driver.page_source)
        self.__upload_to_s3(file_name , f'date={data[-1]}/{folder_name}', html_utf8)

