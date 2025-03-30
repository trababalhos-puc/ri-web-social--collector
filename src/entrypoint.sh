#!/bin/bash
set -e

Xvfb :99 -screen 0 1280x1024x24 &
XVFB_PID=$!
sleep 1
export DISPLAY=:99

echo "Iniciando a aplicação principal..."

"$@"
MAIN_EXIT_CODE=$?

echo "Aplicação principal finalizada com código $MAIN_EXIT_CODE"

echo "Encerrando Xvfb..."
if kill -0 $XVFB_PID 2>/dev/null; then
    kill $XVFB_PID
    wait $XVFB_PID
fi

echo "Todos os processos encerrados, finalizando container..."
exit $MAIN_EXIT_CODE