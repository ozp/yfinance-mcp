#!/usr/bin/env python3
"""Teste final das correções"""

import sys
import json
sys.path.insert(0, '/home/user/yfinance-mcp/src')
from mcp_yfinance.service import YahooFinanceService

service = YahooFinanceService()

print('=' * 70)
print('TESTE COMPLETO APÓS CORREÇÃO')
print('=' * 70)

test_dates = ['2023-06-01', '2023-12-01', '2024-01-15', '2024-06-15', '2025-09-09']
for date in test_dates:
    try:
        result = service.get_stock_price_by_date('AAPL', date)
        data = json.loads(result)
        actual = data['actual_date']
        close = data['close']
        if actual != date:
            print(f'✅ {date}: Close = ${close:.2f} (data de {actual})')
        else:
            print(f'✅ {date}: Close = ${close:.2f}')
    except Exception as e:
        print(f'❌ {date}: {str(e)[:80]}')

print()
print('=' * 70)
print('TESTE DE get_news')
print('=' * 70)
try:
    result = service.get_news('AAPL')
    news = json.loads(result)
    print(f'✅ Encontrou {len(news)} notícias')
    for i, item in enumerate(news[:3]):
        title = item.get('title', 'Sem título')
        print(f'  {i+1}. {title[:60]}...')
except Exception as e:
    print(f'❌ Erro: {e}')

print('\n' + '=' * 70)
