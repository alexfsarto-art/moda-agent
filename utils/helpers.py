""import re
import numpy as np
from typing import Dict, Any


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """Decorator para retry de funções."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time as time_module
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time_module.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        break
            raise last_exception
        return wrapper
    return decorator


def sanitize_price(price_str: str) -> float:
    """Extrai valor numérico de string de preço (R$ 1.299,90 → 1299.90)"""
    if not price_str:
        return 0.0
    # Remove caracteres não numéricos exceto vírgula e ponto
    cleaned = re.sub(r"[^0-9,\.]", "", price_str)
    # Se tem vírgula, é separador decimal
    if ',' in cleaned:
        # Remove pontos de milhar
        cleaned = cleaned.replace('.', '')
        cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def safe_float(val) -> float:
    try:
        return float(val) if val not in (None, '') else 0.0
    except:
        return 0.0


def calculate_competitiveness_score(row: Dict[str, Any], df: 'pd.DataFrame') -> float:
    """Quanto menor o preço relativo à média da categoria, maior a competitividade (0-1)"""
    price = safe_float(row.get('price_num'))
    category = row.get('category', '')
    if price == 0:
        return 0.0

    # Filtra pela mesma categoria
    cat_prices = df[df['category'] == category]['price_num']
    if len(cat_prices) < 2:
        # Se só tem 1 produto na categoria, usar média geral
        cat_prices = df['price_num']

    if len(cat_prices) == 0 or cat_prices.mean() == 0:
        return 0.5

    mean_price = cat_prices.mean()
    # Score: 1 se preço = 0, decresce até 0 quando preço = 3x a média
    ratio = price / mean_price if mean_price else 1
    score = max(0.0, min(1.0, 1.5 - ratio))
    return round(score, 3)


def moving_average(x, window: int = 3):
    if len(x) < window:
        return np.mean(x) if len(x) else 0
    return np.convolve(x, np.ones(window)/window, mode='valid')[0]


def format_currency(value: float) -> str:
    """Formata valor em reais: R$ 1.299,90"""
    try:
        s = f"{value:,.2f}".replace(",", "TMP").replace(".", ",").replace("TMP", ".")
        return f"R$ {s}"
    except:
        return f"R$ {value}"
""