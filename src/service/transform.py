#!/usr/bin/env python3
import concurrent.futures
import json
import logging
import multiprocessing
from pathlib import Path
import os
import html_to_json
from tqdm import tqdm


class HTMLFileMapper:
    def __init__(self, root_dir=None, output_file="html_files_map.json", num_workers=None):
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()

        # Garante que o arquivo de saída seja criado no diretório correto
        if not os.path.isabs(output_file):
            # Se for caminho relativo, cria na raiz do projeto
            self.output_file = os.path.join(self.root_dir, output_file)
        else:
            self.output_file = output_file

        self.result = {"ipea": {}}
        self.num_workers = num_workers if num_workers else multiprocessing.cpu_count()

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def save_json(self):
        """Salva a estrutura de dados em um arquivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(self.result, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Arquivo JSON gerado com sucesso: {self.output_file}")
            file_size = os.path.getsize(self.output_file)
            self.logger.info(f"Tamanho do arquivo: {file_size} bytes")

            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar o arquivo JSON: {e}")
            return False

    def find_ipea_dir(self):
        """
        Encontra o diretório 'ipea' dentro do diretório raiz.

        Returns:
            Path: O caminho para o diretório 'ipea' ou o diretório raiz se não encontrado.
        """
        self.logger.info(f"Procurando diretório 'ipea' em: {self.root_dir}")
        if self.root_dir.name == "ipea":
            self.logger.info("Diretório raiz já é 'ipea'")
            return self.root_dir
        ipea_dirs = list(self.root_dir.glob("**/ipea"))
        if ipea_dirs:
            self.logger.info(f"Diretório 'ipea' encontrado em: {ipea_dirs[0]}")
            return ipea_dirs[0]
        self.logger.warning("Diretório 'ipea' não encontrado. Usando diretório raiz.")
        return self.root_dir

    @staticmethod
    def extract_html_content_date_format(html_file_path):
        """
        Extrai o conteúdo de um arquivo HTML das pastas date= usando html_to_json.

        Args:
            html_file_path (Path): Caminho para o arquivo HTML.

        Returns:
            str: Texto extraído do arquivo HTML ou mensagem de erro.
        """
        try:
            with open(html_file_path, "r", encoding="utf-8") as fp:
                dados = fp.read()

            output_json = html_to_json.convert(dados)
            try:
                content = output_json["html"][0]["body"][0]["form"][0]["table"][0][
                    "tbody"
                ][0]["tr"][0]["td"][1]["_values"]
                extracted_text = "\n".join(content)
                return extracted_text
            except (KeyError, IndexError):
                try:
                    all_values = []

                    def extract_values(obj):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if k == "_values" and isinstance(v, list):
                                    all_values.extend(v)
                                elif isinstance(v, (dict, list)):
                                    extract_values(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                extract_values(item)

                    extract_values(output_json)
                    return (
                        "\n".join(all_values)
                        if all_values
                        else "Nenhum texto encontrado"
                    )
                except Exception as e2:
                    return f"Erro na extração alternativa: {e2}"

        except Exception as e:
            return f"Erro: {e}"

    @staticmethod
    def extract_html_content_pdf_format(html_file_path):
        """
        Extrai o conteúdo de um arquivo HTML das pastas pdf_to_html usando html_to_json.

        Args:
            html_file_path (Path): Caminho para o arquivo HTML.

        Returns:
            str: Texto extraído do arquivo HTML ou mensagem de erro.
        """
        try:
            with open(html_file_path, "r", encoding="utf-8") as fp:
                dados = fp.read()

            output_json = html_to_json.convert(dados)['html'][0]['body'][0]['html'][0]['body'][0]['div']
            _context = str()

            for i in output_json:
                if isinstance(i, dict) and 'p' in i:
                    for x in i['p']:
                        if isinstance(x, dict):
                            if 'b' in x:
                                for b in x['b']:
                                    if isinstance(b, dict) and '_value' in b:
                                        _context += b['_value'] + '\n'
                            elif '_value' in x:
                                _context += x['_value'] + '\n'

            return _context if _context.strip() else "Nenhum texto encontrado"

        except Exception as e:
            try:
                with open(html_file_path, "r", encoding="utf-8") as fp:
                    dados = fp.read()

                output_json = html_to_json.convert(dados)
                all_values = []

                def extract_values(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k == "_value" and isinstance(v, str):
                                all_values.append(v)
                            elif isinstance(v, (dict, list)):
                                extract_values(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_values(item)

                extract_values(output_json)
                return "\n".join(all_values) if all_values else f"Erro na extração: {e}"

            except Exception as e2:
                return f"Erro: {e} | Erro alternativo: {e2}"

    def process_html_file(self, args):
        """
        Processa um único arquivo HTML e retorna suas informações.

        Args:
            args (tuple): Uma tupla contendo (html_file, ipea_dir, extract_content, is_pdf_format)

        Returns:
            tuple: (html_file, file_info) onde file_info é um dicionário com informações do arquivo
        """
        html_file, ipea_dir, extract_content, is_pdf_format = args
        rel_path = html_file.relative_to(ipea_dir)
        file_info = {"path": str(rel_path)}
        if extract_content:
            if is_pdf_format:
                file_info["content"] = self.extract_html_content_pdf_format(html_file)
            else:
                file_info["content"] = self.extract_html_content_date_format(html_file)

        return html_file, file_info

    @staticmethod
    def collect_html_files(ipea_dir):
        """
        Coleta todos os arquivos HTML e organiza-os por diretório, incluindo pdf_to_html.

        Args:
            ipea_dir (Path): Diretório base 'ipea'.

        Returns:
            dict: Dicionário organizado com a estrutura de diretórios e arquivos.
        """
        file_structure = {}
        for date_dir in [d for d in ipea_dir.iterdir() if d.is_dir()]:
            if date_dir.name.startswith("date="):
                date_key = date_dir.name
                file_structure[date_key] = {}
                for subdir in [d for d in date_dir.iterdir() if d.is_dir()]:
                    file_structure[date_key][subdir.name] = {
                        'files': list(subdir.glob("**/*.html")),
                        'is_pdf_format': False
                    }

        pdf_to_html_dir = ipea_dir / "pdf_to_html"
        if pdf_to_html_dir.exists() and pdf_to_html_dir.is_dir():
            file_structure["pdf_to_html"] = {}
            for date_dir in [d for d in pdf_to_html_dir.iterdir() if d.is_dir()]:
                if date_dir.name.startswith("date="):
                    date_key = date_dir.name
                    file_structure["pdf_to_html"][date_key] = {
                        'files': list(date_dir.glob("**/*.html")),
                        'is_pdf_format': True
                    }

        return file_structure

    def map_html_files(self, extract_content=True):
        """
        Mapeia todos os arquivos HTML a partir do diretório 'ipea' e cria uma estrutura JSON.
        Utiliza processamento paralelo para melhorar a performance.

        Args:
            extract_content (bool): Se True, extrai o conteúdo de cada arquivo HTML.

        Returns:
            dict: Estrutura de dados contendo o mapeamento dos arquivos HTML.
        """
        if not self.root_dir.exists() or not self.root_dir.is_dir():
            self.logger.error(
                f"O diretório {self.root_dir} não existe ou não é um diretório."
            )
            return self.result

        ipea_dir = self.find_ipea_dir()
        file_structure = self.collect_html_files(ipea_dir)

        for main_key, subdirs in file_structure.items():
            self.result["ipea"][main_key] = {}
            if main_key == "pdf_to_html":
                for date_key in subdirs:
                    self.result["ipea"][main_key][date_key] = {}
            else:
                for subdir_name in subdirs:
                    self.result["ipea"][main_key][subdir_name] = {}

        all_files = []
        for main_key, subdirs in file_structure.items():
            if main_key == "pdf_to_html":
                for date_key, file_info in subdirs.items():
                    for html_file in file_info['files']:
                        all_files.append((html_file, ipea_dir, extract_content, file_info['is_pdf_format']))
            else:
                for subdir_name, file_info in subdirs.items():
                    for html_file in file_info['files']:
                        all_files.append((html_file, ipea_dir, extract_content, file_info['is_pdf_format']))

        total_files = len(all_files)
        self.logger.info(f"Encontrados {total_files} arquivos HTML para processamento")

        if total_files > 0:
            self.logger.info(
                f"Iniciando processamento paralelo com {self.num_workers} workers"
            )

            processed_files = 0
            with concurrent.futures.ProcessPoolExecutor(
                    max_workers=self.num_workers
            ) as executor:
                batch_size = max(1, min(1000, total_files // 10))

                for i in range(0, total_files, batch_size):
                    batch = all_files[i : i + batch_size]
                    self.logger.info(
                        f"Processando lote {i//batch_size + 1}/{(total_files-1)//batch_size + 1}"
                    )
                    results = list(
                        tqdm(
                            executor.map(self.process_html_file, batch),
                            total=len(batch),
                            desc="Processando arquivos HTML",
                        )
                    )

                    for html_file, file_info in results:
                        processed_files += 1
                        rel_path = html_file.relative_to(ipea_dir)
                        parts = rel_path.parts

                        if len(parts) >= 2:
                            if parts[0] == "pdf_to_html" and len(parts) >= 3:
                                main_key = parts[0]
                                date_key = parts[1]

                                if (main_key in self.result["ipea"] and
                                        date_key in self.result["ipea"][main_key]):
                                    self.result["ipea"][main_key][date_key][html_file.name] = file_info
                            else:
                                date_key = parts[0]
                                subdir_name = parts[1]

                                if (date_key in self.result["ipea"] and
                                        subdir_name in self.result["ipea"][date_key]):
                                    self.result["ipea"][date_key][subdir_name][html_file.name] = file_info

                    self.logger.info(
                        f"Progresso: {processed_files}/{total_files} arquivos processados"
                    )

            self.logger.info(
                f"Processamento paralelo concluído. Total de {processed_files} arquivos processados."
            )

        return self.result

    def run(self, extract_content=True):
        """
        Executa o processo completo de mapeamento e salvamento.

        Args:
            extract_content (bool): Se True, extrai o conteúdo de cada arquivo HTML.

        Returns:
            dict: A estrutura de dados contendo o mapeamento.
        """
        self.logger.info(
            f"Iniciando mapeamento de arquivos HTML usando {self.num_workers} processos paralelos..."
        )
        self.map_html_files(extract_content=extract_content)
        self.save_json()
        return self.result
