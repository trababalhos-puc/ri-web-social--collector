#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: drive.py
~~~~~~~~~~~~~~~~~

inicializar o WebDriver Selenium (DriverManager).
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:author: AriHenrique
:date: 2025-03-04
"""

import logging
from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DriverManager:
    """
    Classe responsável por inicializar o WebDriver do Selenium.
    """

    def __init__(self):
        """
        Construtor da classe DriverManager.
        """
        self.driver = None

    def start_driver(self, headless: bool = False):
        """
        Inicia o driver do Selenium para Chrome, aplicando opções padrão
        e permitindo a execução em modo headless.

        :param headless: Define se o navegador deve ser iniciado sem interface gráfica.
                         Padrão: False.
        :type headless: bool
        :return: Instância do WebDriver configurado.
        :rtype: selenium.webdriver.Chrome
        """
        chrome_service = Service(ChromeDriverManager().install())
        chrome_options = Options()

        default_options = [
            '--disable-gpu',
            '--ignore-certificate-errors',
            '--disable-extensions',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ]

        if headless:
            chrome_options.add_argument('--headless')

        for option in default_options:
            chrome_options.add_argument(option)
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        return self.driver