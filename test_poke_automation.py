import requests
import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

# Configurações do Agente de Teste
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
TARGETS = ["pikachu", "charizard", "bulbasaur", "squirtle", "mewtwo"]

# 1. Teste Funcional e de Contrato
@pytest.mark.parametrize("poke_name", TARGETS)
def test_poke_api_contract(poke_name):
    response = requests.get(f"{BASE_URL}{poke_name}")
    assert response.status_code == 200
    data = response.json()
    
    # Validação de Contrato (Tipagem)
    assert isinstance(data['name'], str)
    assert isinstance(data['id'], int)
    assert "abilities" in data

# 2. Teste de Performance com Latência P95
def test_performance_p95():
    latencias = []
    
    def make_request():
        start = time.perf_counter()
        requests.get(f"{BASE_URL}pikachu")
        return time.perf_counter() - start

    # Simula 20 requisições simultâneas
    with ThreadPoolExecutor(max_workers=5) as executor:
        resultados = list(executor.map(lambda f: f(), [make_request] * 20))
    
    latencias = [r * 1000 for r in resultados] # Converte para ms
    p95 = statistics.quantiles(latencias, n=100)[94] # Calcula o percentil 95
    
    print(f"\n⏱️ Latência Média: {statistics.mean(latencias):.2f}ms")
    print(f"🚀 Latência P95 (Pior cenário): {p95:.2f}ms")
    
    # O teste falha se 95% das requisições demorarem mais de 800ms
    assert p95 < 800, f"Performance inaceitável: P95 de {p95}ms"

if __name__ == "__main__":
    pytest.main([__file__, "-s"])