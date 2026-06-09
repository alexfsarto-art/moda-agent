""import requests
import time
from typing import List, Dict, Any
from config import MARITACA_API_KEY, MARITAVA_BASE_URL, ANALYSIS_CONFIG, DEFAULT_HEADERS
from utils.scrapers import GoogleTrendsScraper, InstagramScraper
from utils.helpers import retry_on_failure


class TrendAnalyzer:
    def __init__(self, keywords: List[str], platforms=None):
        self.keywords = keywords
        self.platforms = platforms or ["google_trends", "instagram"]
        self.gts = GoogleTrendsScraper()
        self.isc = InstagramScraper()

    @retry_on_failure(max_attempts=3, delay=2)
    def _query_maritava(self, prompt: str) -> Dict[str, Any]:
        if not MARITACA_API_KEY:
            return {}
        url = f"{MARITAVA_BASE_URL}/v1/chat/completions"
        payload = {
            "model": "sabiá-4",
            "messages": [
                {"role": "system", "content": "Você é um analista de tendências de moda especializado no mercado brasileiro."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        headers = {
            "Authorization": f"Bearer {MARITACA_API_KEY}",
            "Content-Type": "application/json"
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def analyze_trends(self) -> Dict[str, Any]:
        """Busca tendências em múltiplas fontes e consolida com IA."""
        results = {}

        # Google Trends
        if "google_trends" in self.platforms:
            print("📈 Coletando dados do Google Trends...")
            gt_data = self.gts.get_trends(self.keywords, ANALYSIS_CONFIG["trend_window_days"])
            results["google_trends"] = gt_data

        # Instagram (hashtags)
        if "instagram" in self.platforms:
            print("📸 Coletando dados do Instagram...")
            ig_data = self.isc.get_hashtag_stats(self.keywords)
            results["instagram"] = ig_data

        # Análise com Maritava AI
        if MARITACA_API_KEY:
            print("🧠 Analisando tendências com Maritava AI...")
            prompt = (
                f"Considere os seguintes dados de tendências de moda. Identifique os 5 temas emergentes mais relevantes, "
                f"as categorias de produtos com maior potencial de venda e as regiões geográficas com maior interesse. "
                f"Dados: {str(results)} "
                f"Foque no mercado brasileiro e em tendências para os próximos 3 meses."
            )
            ai_response = self._query_maritava(prompt)
            results["maritava_analysis"] = ai_response

        return results

    def run(self) -> Dict[str, Any]:
        """Executa o fluxo completo de análise de tendências."""
        raw_data = self.analyze_trends()

        # Extrair insights estruturados
        trends = raw_data.get("maritava_analysis", {})
        if isinstance(trends, dict) and "choices" in trends:
            content = trends["choices"][0]["message"]["content"]
        else:
            # Fallback: usar os dados brutos se não houver IA
            content = str(raw_data)

        # Estruturar output
        return {
            "raw_data": raw_data,
            "emerging_themes": self._extract_themes(content),
            "hot_categories": self._extract_categories(content),
            "suggested_keywords": self._extract_suggested_keywords(content),
            "analysis_timestamp": time.time()
        }

    def _extract_themes(self, content: str) -> List[str]:
        # Heurística simples — em produção, usar parser mais robusto
        import re
        matches = re.findall(r"(?:tema|tendência|categoria emergente)[s]?[:\s-]+([A-Za-zÀ-ú\s]+)(?=\.|,|\n|$)", content, re.I)
        themes = [m.strip() for m in matches]
        if not themes:
            # Fallback: pegar 3 frases-chave
            themes = [s.strip() for s in content.split(".") if "tema" in s.lower() or "tendência" in s.lower()][:3]
        return themes[:5] or ["Análise de tendências disponível no relatório completo"]

    def _extract_categories(self, content: str) -> List[str]:
        import re
        matches = re.findall(r"(?:categoria|produto|segmento)[s]?[:\s-]+([A-Za-zÀ-ú\s]+)(?=\.|,|\n|$)", content, re.I)
        cats = [m.strip() for m in matches]
        return cats[:8]

    def _extract_suggested_keywords(self, content: str) -> List[str]:
        import re
        # Procura listas de keywords sugeridas
        pattern = r"(?:palavras-chave|keywords|buscas sugeridas)[:\s]*([\w\s,À-ú-]+)(?=\n|$)"
        matches = re.findall(pattern, content, re.I)
        if matches:
            kw_list = [k.strip() for k in matches[0].split(",")]
            return kw_list[:10]
        return self.keywords[:10]
""