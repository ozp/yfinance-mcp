#!/usr/bin/env python3
"""
Diagnóstico completo do erro get_stock_price_by_date
"""

import sys
from datetime import datetime, timedelta
import yfinance as yf
from requests import Session

print("=" * 60)
print("DIAGNÓSTICO: get_stock_price_by_date")
print("=" * 60)

# Teste 1: Yahoo Finance direto (sem User-Agent)
print("\n1. TESTE: yfinance direto (sem User-Agent)")
print("-" * 60)
try:
    ticker = yf.Ticker("AAPL")
    date = "2024-01-15"
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    hist = ticker.history(start=date, end=end_date, interval="1d")
    print(f"✅ Sucesso! Retornou {len(hist)} registros")
    print(f"Dados: {hist}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 2: Yahoo Finance com User-Agent
print("\n2. TESTE: yfinance com User-Agent")
print("-" * 60)
try:
    session = Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/124.0.0.0 Safari/537.36'
    })

    ticker = yf.Ticker("AAPL", session=session)
    date = "2024-01-15"
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    hist = ticker.history(start=date, end=end_date, interval="1d")
    print(f"✅ Sucesso! Retornou {len(hist)} registros")
    print(f"Dados: {hist}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 3: Múltiplas datas
print("\n3. TESTE: Múltiplas datas (com User-Agent)")
print("-" * 60)
test_dates = [
    "2024-01-15",
    "2024-06-15",
    "2023-12-01",
    "2023-06-01"
]

session = Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/124.0.0.0 Safari/537.36'
})

for date in test_dates:
    try:
        ticker = yf.Ticker("AAPL", session=session)
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

        hist = ticker.history(start=date, end=end_date, interval="1d")

        if hist.empty:
            # Tentar buscar 7 dias atrás
            start_search = (date_obj - timedelta(days=7)).strftime("%Y-%m-%d")
            hist = ticker.history(start=start_search, end=end_date, interval="1d")
            print(f"⚠️  {date}: Sem dados diretos, buscou 7 dias atrás -> {len(hist)} registros")
        else:
            print(f"✅ {date}: {len(hist)} registros")

    except Exception as e:
        print(f"❌ {date}: Erro - {e}")

# Teste 4: Verificar estrutura dos dados retornados
print("\n4. TESTE: Estrutura dos dados")
print("-" * 60)
try:
    session = Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/124.0.0.0 Safari/537.36'
    })

    ticker = yf.Ticker("AAPL", session=session)
    date = "2024-01-15"
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    hist = ticker.history(start=date, end=end_date, interval="1d")

    print(f"Tipo: {type(hist)}")
    print(f"Shape: {hist.shape}")
    print(f"Colunas: {hist.columns.tolist()}")
    print(f"Index type: {type(hist.index)}")
    print(f"\nPrimeiras linhas:")
    print(hist.head())

except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 5: Testar o serviço real
print("\n5. TESTE: Usando o serviço YFinanceService")
print("-" * 60)
try:
    sys.path.insert(0, '/home/user/yfinance-mcp/src')
    from mcp_yfinance.service import YFinanceService

    service = YFinanceService()
    result = service.get_stock_price_by_date("AAPL", "2024-01-15")
    print(f"✅ Sucesso!")
    print(result)
except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
