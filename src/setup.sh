#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "Este script precisa ser executado como root. Use sudo."
    exit 1
fi

echo "Atualizando lista de pacotes..."
apt-get update

echo "Instalando dependências necessárias..."
apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    tesseract-ocr \
    poppler-utils \
    xdg-utils

echo "Baixando e adicionando chave de repositório do Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

echo "Adicionando repositório do Google Chrome..."
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

echo "Atualizando lista de pacotes novamente..."
apt-get update

echo "Instalando Google Chrome..."
apt-get install -y google-chrome-stable

echo "Limpando arquivos temporários..."
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "Instalação concluída!"