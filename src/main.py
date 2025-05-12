import os
import multiprocessing
from service.extract import IPEAExtractor
from service.index import Index
from service.transform import HTMLFileMapper

BUCKET = os.getenv(
    "BUCKET_NAME",
    # "prod-ri-web-social--collector--trab",
    None,
)


def lambda_handler(event, context):

    ind_periodos = [7, 11, 39, 9]

    ind_temas = [
        10,
        7,
        5,
        2,
        8,
        11,
        12,
        19,
        6,
        39,
        15,
        3,
        27,
        14,
        9,
        1,
        16,
        13,
        17,
        33,
    ]

    list_periodo = [
        f"IrParaModuloPagina('M', 'Ser_TemasPer({i}, -1)')" for i in ind_periodos
    ]
    list_temas = [f"IrParaModuloPagina('M', 'Ser_Temas({i})')" for i in ind_temas]
    # list_periodo = []
    list_js = list_periodo + list_temas

    prefix = "ipea/"

    for js in list_js:
        extractor = IPEAExtractor(js, BUCKET, prefix, headless=True)
        extractor.run_extraction()

    return {
        "statusCode": 200,
        "body": "Extração e envio para o S3 concluídos com sucesso.",
    }


if __name__ == "__main__":
    lambda_handler(None, None)
