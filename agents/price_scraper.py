import requests
import time
from typing import List, Dict, Any
from config import DEFAULT_HEADERS, ANALYSIS_CONFIG
from utils.scrapers import MercadoLivreScraper, ShopeeScraper, MagaluScraper, AmazonScraper
from utils.helpers import retry_on_failure, sanitize_price


class PriceScraper:
    def __init__(self, platforms=None):
        self.platforms = platforms or ["mercado_livre", "shopee", "magalu", "amazon"]
        self.scrapers = {
            "mercado_livre": MercadoLivreScraper(),
            "shopee": ShopeeScraper(),
            "magalu": MagaluScraper(),
            "amazon": AmazonScraper(),
        }

    def run(self, keywords: List[str], limit: int = 20) -> Dict[str, Any]:
        """Coleta produtos e preços de todas as plataformas configuradas."""
        results = {}
        total_products = 0

        for platform in self.platforms:
            if platform not in self.scrapers:
                print(f"⚠️  Scraper não implementado para {platform}")
                continue

            print(f"🛒 Buscando em {platform.replace('_', ' ').title()}...")
            scraper = self.scrapers[platform]
            platform_products = []

            for kw in keywords:
                try:
                    products = scraper.search(kw, limit=limit // len(keywords) + 5)
                    platform_products.extend(products)
                    time.sleep(1)  # Respeitar rate limit
                except Exception as e:
                    print(f"Erro ao buscar '{kw}' em {platform}: {e}")

            # Remover duplicatas por link/título
            unique_products = self._deduplicate(platform_products)
            results[platform] = unique_products[:limit]
            total_products += len(unique_products)
            print(f"✅ {len(unique_products)} produtos únicos encontrados em {platform}")

        print(f"✨ Total: {total_products} produtos coletados em todas as plataformas")
        return results

    def _deduplicate(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique = []
        for p in products:
            key = p.get("url") or p.get("title", "") or str(p)
            # Hash mais robusto
            hash_key = (key[:100] + p.get("platform", ""))[:120]
            if hash_key not in seen:
                seen.add(hash_key)
                unique.append(p)
        return unique
