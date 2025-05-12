import logging
import multiprocessing

from service.index import Index
from service.transform import HTMLFileMapper

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        num_cpus = max(1, multiprocessing.cpu_count() // 2)
        logger.info(f"Iniciando processamento com {num_cpus} processos paralelos")
        mapper = HTMLFileMapper(num_workers=num_cpus)
        result = mapper.run(extract_content=True)
        logger.info(
            f"Mapeamento de arquivos HTML concluído. Arquivo de saída: {mapper.output_file}"
        )

        analyzer = Index(mapper.output_file).start()

        if analyzer:
            analyzer.compare_indices()
            logger.info(
                "Processamento completo e análise de índices finalizada com sucesso."
            )
        else:
            logger.error("Não foi possível criar o analisador de índices.")

    except Exception as e:
        logger.error(f"Erro durante a execução: {e}", exc_info=True)
