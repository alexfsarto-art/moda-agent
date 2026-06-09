""import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any
from config import DEFAULT_HEADERS
from utils.helpers import sanitize_price, safe_float

# --- Google Trends e Instagram (mocks) ---
class GoogleTrendsScraper:
    def get_trends(self, keywords: List[str], days: int = 30) -> Dict[str, Any]:
        import random
        results = {}
        for kw in keywords:
            results[kw] = {
                "interest_over_time": {"last_30_days": random.randint(50, 100)},
                "related_queries": [f"{kw} barato", f"{kw} feminino", f"promoção {kw}"]
            }
        return results


class InstagramScraper:
    def get_hashtag_stats(self, keywords: List[str]) -> Dict[str, Any]:
        import random
        results = {}
        for kw in keywords:
            hashtag = kw.replace(' ', '').lower()
            results[kw] = {
                "hashtag": f"#{hashtag}",
                "posts": random.randint(10000, 500000),
                "growth_rate": random.uniform(0.05, 0.35)
            }
        return results


# --- Mercado Livre ---
class MercadoLivreScraper:
    def search(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        products = []
        try:
            url = f"https://lista.mercadolivre.com.br/{keyword.replace(' ', '-')}"
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            if resp.status_code != 200:
                return products

            soup = BeautifulSoup(resp.text, "lxml")
            items = soup.select("li.ui-search-result")[:limit]

            for item in items:
                title_elem = item.select_one(".ui-search-item__title")
                price_elem = item.select_one(".ui-search-price__second-line")
                link_elem = item.select_one("a.ui-search-link")
                sales_elem = item.select_one(".ui-search-item__sold")

                if not title_elem or not price_elem or not link_elem:
                    continue

                title = title_elem.text.strip()
                price_str = price_elem.text.strip()
                price = sanitize_price(price_str)
                url = link_elem['href']
                sales_text = sales_elem.text.strip() if sales_elem else "0 vendidos"
                sales = int(''.join(filter(str.isdigit, sales_text))) if sales_text else 0
                category = self._guess_category(title, keyword)

                products.append({
                    "title": title,
                    "price": price,
                    "rating": None,
                    "sales": sales,
                    "platform": "mercado_livre",
                    "url": url,
                    "category": category
                })
        except Exception as e:
            print(f"Erro Mercado Livre ({keyword}): {e}")
        return products

    def _guess_category(self, title: str, keyword: str) -> str:
        title_lower = title.lower()
        cats = {
            "vestido": "Vestuário Feminino",
            "calça": "Vestuário Feminino",
            "blusa": "Vestuário Feminino",
            "sapato": "Calçados",
            "tênis": "Calçados",
            "bolsa": "Acessórios",
            "relógio": "Acessórios",
            "shorts": "Vestuário Feminino",
            "camisa": "Vestuário Masculino",
            "bermuda": "Vestuário Masculino",
            "jaqueta": "Vestuário",
            "moletom": "Vestuário",
            "casaco": "Vestuário",
            "acessório": "Acessórios",
        }
        for k, v in cats.items():
            if k in title_lower:
                return v
        return keyword.split()[0].capitalize() if keyword else "Não classificado"


# --- Shopee ---
class ShopeeScraper:
    def search(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        products = []
        try:
            # Shopee usa API pública (mobile)
            api_url = f"https://shopee.com.br/api/v4/search/search_items?keyword={requests.utils.quote(keyword)}&limit={limit}&offset=0"
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = "https://shopee.com.br/"
            headers['X-Requested-With'] = "XMLHttpRequest"

            resp = requests.get(api_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                return products

            data = resp.json()
            items = data.get('items', [])

            for item in items:
                item_data = item.get('item_basic', {})
                title = item_data.get('name', '')
                price_raw = item_data.get('price', 0)
                # Preço em centavos
                price = (price_raw / 100000) if price_raw else 0
                if price == 0:
                    price = sanitize_price(item_data.get('price_before_discount', '0'))

                item_id = item_data.get('item_id')
                shop_id = item_data.get('shop_id')
                url = f"https://shopee.com.br/pd/{item_id}?s={shop_id}" if item_id and shop_id else ""
                sales = item_data.get('sold', 0)
                rating = item_data.get('rating_star', None)
                category = item_data.get('category_name', self._guess_category(title, keyword))

                products.append({
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "sales": sales,
                    "platform": "shopee",
                    "url": url,
                    "category": category
                })
        except Exception as e:
            print(f"Erro Shopee ({keyword}): {e}")
        return products

    def _guess_category(self, title: str, keyword: str) -> str:
        # Mesma lógica do ML
        title_lower = title.lower()
        cats = {
            "vestido": "Vestuário Feminino",
            "calça": "Vestuário Feminino",
            "blusa": "Vestuário Feminino",
            "sapato": "Calçados",
            "tênis": "Calçados",
            "bolsa": "Acessórios",
            "shorts": "Vestuário Feminino",
            "camisa": "Vestuário Masculino",
        }
        for k, v in cats.items():
            if k in title_lower:
                return v
        return "Moda"


# --- Magalu ---
class MagaluScraper:
    def search(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        products = []
        try:
            url = f"https://www.magazineluiza.com.br/busca/{keyword.replace(' ', '+')}"
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            if resp.status_code != 200:
                return products

            soup = BeautifulSoup(resp.text, "lxml")
            # Magalu usa data-testid ou classes dinâmicas — usar fallback
            items = soup.select("div[data-testid='product-card']") or soup.select(".product-li")
            if not items:
                items = soup.select(".product")

            for item in items[:limit]:
                title_elem = item.select_one(".product-title") or item.select_one("h2") or item.select_one("[data-testid='product-title']")
                price_elem = item.select_one(".price-value") or item.select_one(".price") or item.select_one(".sc-eBMEME")
                link_elem = item.select_one("a")

                if not title_elem or not price_elem or not link_elem:
                    continue

                title = title_elem.text.strip()
                price_str = price_elem.text.strip()
                price = sanitize_price(price_str)
                base_url = "https://www.magazineluiza.com.br"
                url = base_url + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']
                category = self._guess_category(title, keyword)

                # Magalu não expõe vendas/rating facilmente via HTML
                products.append({
                    "title": title,
                    "price": price,
                    "rating": None,
                    "sales": None,
                    "platform": "magalu",
                    "url": url,
                    "category": category
                })
        except Exception as e:
            print(f"Erro Magalu ({keyword}): {e}")
        return products

    def _guess_category(self, title: str, keyword: str) -> str:
        title_lower = title.lower()
        cats = {
            "vestido": "Vestuário Feminino",
            "calça": "Vestuário Feminino",
            "blusa": "Vestuário Feminino",
            "sapato": "Calçados",
            "tênis": "Calçados",
            "bolsa": "Acessórios",
        }
        for k, v in cats.items():
            if k in title_lower:
                return v
        return "Moda"


# --- Amazon ---
class AmazonScraper:
    def search(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        products = []
        try:
            url = f"https://www.amazon.com.br/s?k={requests.utils.quote(keyword)}&language=pt-BR"
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            if resp.status_code != 200:
                return products

            soup = BeautifulSoup(resp.text, "lxml")
            items = soup.select("div.s-result-item")[:limit]

            for item in items:
                title_elem = item.select_one("h2")
                price_whole = item.select_one(".a-price-whole")
                price_frac = item.select_one(".a-price-fraction")
                link_elem = item.select_one("a.a-link-normal")
                rating_elem = item.select_one(".a-icon-alt")

                if not title_elem or not link_elem:
                    continue

                title = title_elem.text.strip()
                url = "https://www.amazon.com.br" + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']

                # Preço
                if price_whole and price_frac:
                    price_str = f"{price_whole.text.strip()}.{price_frac.text.strip().rstrip('0').rstrip('.')}".replace('.', '').replace(',', '.')
                    price = sanitize_price(price_str)
                else:
                    price = 0.0

                # Rating
                rating = None
                if rating_elem and rating_elem.text:
                    match = re.search(r"([0-9,.]+) de 5 estrelas", rating_elem.text)
                    if match:
                        rating = float(match.group(1).replace(',', '.'))

                # Vendas não expostas
                category = self._guess_category(title, keyword)

                products.append({
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "sales": None,
                    "platform": "amazon",
                    "url": url,
                    "category": category
                })
        except Exception as e:
            print(f"Erro Amazon ({keyword}): {e}")
        return products

    def _guess_category(self, title: str, keyword: str) -> str:
        title_lower = title.lower()
        cats = {
            "vestido": "Vestuário Feminino",
            "calça": "Vestuário Feminino",
            "blusa": "Vestuário Feminino",
            "sapato": "Calçados",
            "tênis": "Calçados",
            "bolsa": "Acessórios",
            "relógio": "Acessórios",
        }
        for k, v in cats.items():
            if k in title_lower:
                return v
        return "Moda"
""