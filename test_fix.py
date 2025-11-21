#!/usr/bin/env python3
"""
Teste da correção: Não passar Session, deixar yfinance gerenciar
"""

import yfinance as yf
from datetime import datetime, timedelta

print("=" * 60)
print("TESTE DA CORREÇÃO")
print("=" * 60)

# Teste 1: SEM passar session (deixar yfinance gerenciar)
print("\n1. TESTE: yfinance SEM passar session")
print("-" * 60)
try:
    ticker = yf.Ticker("AAPL")  # SEM session parameter
    date = "2023-12-15"  # Data no passado
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    hist = ticker.history(start=date, end=end_date, interval="1d")
    print(f"✅ Sucesso! Retornou {len(hist)} registros")
    if not hist.empty:
        print(f"\nDados para {date}:")
        print(hist)
    else:
        print(f"⚠️  Sem dados para {date}, tentando buscar últimos 7 dias...")
        start_search = (date_obj - timedelta(days=7)).strftime("%Y-%m-%d")
        hist = ticker.history(start=start_search, end=end_date, interval="1d")
        print(f"Retornou {len(hist)} registros dos últimos 7 dias")
        print(hist)
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 2: Múltiplas datas
print("\n2. TESTE: Múltiplas datas SEM session")
print("-" * 60)
test_dates = [
    "2023-06-01",
    "2023-12-01",
    "2024-01-15",
    "2024-06-15"
]

for date in test_dates:
    try:
        ticker = yf.Ticker("AAPL")
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

        hist = ticker.history(start=date, end=end_date, interval="1d")

        if hist.empty:
            start_search = (date_obj - timedelta(days=7)).strftime("%Y-%m-%d")
            hist = ticker.history(start=start_search, end=end_date, interval="1d")
            if not hist.empty:
                print(f"✅ {date}: Encontrou {len(hist)} registros nos últimos 7 dias")
            else:
                print(f"❌ {date}: Sem dados mesmo nos últimos 7 dias")
        else:
            print(f"✅ {date}: {len(hist)} registros diretos")

    except Exception as e:
        print(f"❌ {date}: Erro - {e}")

# Teste 3: Verificar versão do yfinance
print("\n3. INFORMAÇÕES DO AMBIENTE")
print("-" * 60)
print(f"yfinance version: {yf.__version__}")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
