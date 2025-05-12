#!/usr/bin/env python3
import json
from pathlib import Path
import logging
import html_to_json
import concurrent.futures
import multiprocessing
from tqdm import tqdm

class HTMLFileMapper:
    """
    Classe para mapear arquivos HTML em uma estrutura de diretórios e gerar um JSON
    que reflete a hierarquia de diretórios no formato ipea > date=... > arquivo.html
    """

    def __init__(self, root_dir=None, output_file='html_files_map.json', num_workers=None):
        """
        Inicializa o mapeador de arquivos HTML.

        Args:
            root_dir (str): Diretório raiz para iniciar a pesquisa. Se None, usa o diretório atual.
            output_file (str): Nome do arquivo JSON de saída.
            num_workers (int): Número de processos paralelos a serem usados. Se None, usa o número de CPUs.
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.output_file = output_file
        self.result = {'ipea': {}}
        self.num_workers = num_workers if num_workers else multiprocessing.cpu_count()

        # Configuração de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def find_ipea_dir(self):
        """
        Encontra o diretório 'ipea' dentro do diretório raiz.

        Returns:
            Path: O caminho para o diretório 'ipea' ou o diretório raiz se não encontrado.
        """
        self.logger.info(f"Procurando diretório 'ipea' em: {self.root_dir}")
        if self.root_dir.name == 'ipea':
            self.logger.info("Diretório raiz já é 'ipea'")
            return self.root_dir
        ipea_dirs = list(self.root_dir.glob('**/ipea'))
        if ipea_dirs:
            self.logger.info(f"Diretório 'ipea' encontrado em: {ipea_dirs[0]}")
            return ipea_dirs[0]
        self.logger.warning("Diretório 'ipea' não encontrado. Usando diretório raiz.")
        return self.root_dir

    @staticmethod
    def extract_html_content(html_file_path):
        """
        Extrai o conteúdo de um arquivo HTML usando html_to_json.

        Args:
            html_file_path (Path): Caminho para o arquivo HTML.

        Returns:
            str: Texto extraído do arquivo HTML ou mensagem de erro.
        """
        try:
            with open(html_file_path, 'r', encoding='utf-8') as fp:
                dados = fp.read()

            output_json = html_to_json.convert(dados)
            try:
                content = output_json['html'][0]['body'][0]['form'][0]['table'][0]['tbody'][0]['tr'][0]['td'][1]['_values']
                extracted_text = "\n".join(content)
                return extracted_text
            except (KeyError, IndexError) as e:
                # Se não conseguir encontrar a estrutura exata, tenta uma abordagem mais genérica
                # Abordagem alternativa - tenta extrair todos os valores de texto
                try:
                    all_values = []
                    def extract_values(obj):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if k == '_values' and isinstance(v, list):
                                    all_values.extend(v)
                                elif isinstance(v, (dict, list)):
                                    extract_values(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                extract_values(item)

                    extract_values(output_json)
                    return "\n".join(all_values) if all_values else "Nenhum texto encontrado"
                except Exception as e2:
                    return f"Erro na extração alternativa: {e2}"

        except Exception as e:
            return f"Erro: {e}"

    def process_html_file(self, args):
        """
        Processa um único arquivo HTML e retorna suas informações.

        Args:
            args (tuple): Uma tupla contendo (html_file, ipea_dir, extract_content)

        Returns:
            tuple: (html_file, file_info) onde file_info é um dicionário com informações do arquivo
        """
        html_file, ipea_dir, extract_content = args
        rel_path = html_file.relative_to(ipea_dir)
        file_info = {
            "path": str(rel_path)
        }
        if extract_content:
            file_info["content"] = self.extract_html_content(html_file)

        return html_file, file_info

    @staticmethod
    def collect_html_files(ipea_dir):
        """
        Coleta todos os arquivos HTML e organiza-os por diretório.

        Args:
            ipea_dir (Path): Diretório base 'ipea'.

        Returns:
            dict: Dicionário organizado com a estrutura de diretórios e arquivos.
        """
        file_structure = {}
        for date_dir in [d for d in ipea_dir.iterdir() if d.is_dir()]:
            if date_dir.name.startswith('date='):
                date_key = date_dir.name
                file_structure[date_key] = {}
                for subdir in [d for d in date_dir.iterdir() if d.is_dir()]:
                    file_structure[date_key][subdir.name] = list(subdir.glob('**/*.html'))

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
        # Verifica se o diretório existe
        if not self.root_dir.exists() or not self.root_dir.is_dir():
            self.logger.error(f"O diretório {self.root_dir} não existe ou não é um diretório.")
            return self.result
        ipea_dir = self.find_ipea_dir()
        file_structure = self.collect_html_files(ipea_dir)
        for date_key, subdirs in file_structure.items():
            self.result['ipea'][date_key] = {}
            for subdir_name in subdirs:
                self.result['ipea'][date_key][subdir_name] = {}
        all_files = []
        for date_key, subdirs in file_structure.items():
            for subdir_name, html_files in subdirs.items():
                for html_file in html_files:
                    all_files.append((html_file, ipea_dir, extract_content))

        total_files = len(all_files)
        self.logger.info(f"Encontrados {total_files} arquivos HTML para processamento")
        if total_files > 0:
            self.logger.info(f"Iniciando processamento paralelo com {self.num_workers} workers")

            processed_files = 0
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                batch_size = max(1, min(1000, total_files // 10))

                for i in range(0, total_files, batch_size):
                    batch = all_files[i:i+batch_size]
                    self.logger.info(f"Processando lote {i//batch_size + 1}/{(total_files-1)//batch_size + 1}")
                    results = list(tqdm(
                        executor.map(self.process_html_file, batch),
                        total=len(batch),
                        desc="Processando arquivos HTML"
                    ))
                    for html_file, file_info in results:
                        processed_files += 1
                        rel_path = html_file.relative_to(ipea_dir)
                        parts = rel_path.parts

                        if len(parts) >= 2:
                            date_key = parts[0]
                            subdir_name = parts[1]

                            if date_key in self.result['ipea'] and subdir_name in self.result['ipea'][date_key]:
                                self.result['ipea'][date_key][subdir_name][html_file.name] = file_info

                    self.logger.info(f"Progresso: {processed_files}/{total_files} arquivos processados")

            self.logger.info(f"Processamento paralelo concluído. Total de {processed_files} arquivos processados.")

        return self.result

    def save_json(self):
        """
        Salva a estrutura de dados em um arquivo JSON.

        Returns:
            bool: True se o salvamento foi bem-sucedido, False caso contrário.
        """
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.result, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Arquivo JSON gerado com sucesso: {self.output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar o arquivo JSON: {e}")
            return False

    def run(self, extract_content=True):
        """
        Executa o processo completo de mapeamento e salvamento.

        Args:
            extract_content (bool): Se True, extrai o conteúdo de cada arquivo HTML.

        Returns:
            dict: A estrutura de dados contendo o mapeamento.
        """
        self.logger.info(f"Iniciando mapeamento de arquivos HTML usando {self.num_workers} processos paralelos...")
        self.map_html_files(extract_content=extract_content)
        self.save_json()
        return self.result