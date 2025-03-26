"""Configurações globais para testes com pytest."""
import pytest

@pytest.fixture
def exemplo_fixture():
    """Exemplo de fixture para testes."""
    # Configuração
    yield "dados_exemplo"
    # Limpeza
