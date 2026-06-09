""import os
from dotenv import load_dotenv

load_dotenv()

# Maritaca AI
MARITACA_API_KEY = os.getenv("MARITACA_API_KEY")
MARITAVA_BASE_URL = os.getenv("MARITAVA_BASE_URL", "https://api.maritaca.ai")

# Plataformas de busca
SEARCH_PLATFORMS = [
    "google_trends",
    "instagram",
    "mercado_livre",
    "shopee",
    "amazon",
    "magalu"
]

# Configurações de análise
ANALYSIS_CONFIG = {
    "trend_window_days": 30,
    "min_sales_threshold": 50,
    "price_competitiveness_threshold": 0.8,
    "top_products_limit": 20,
    "trend_keywords": [
        "moda primavera verão",
        "tendências 2026",
        "roupas femininas mais vendidas",
        "calçados tendência",
        "acessórios moda",
        "streetwear Brasil",
        "moda sustentável",
        "outlet online"
    ]
}

# Caminhos
DATA_RAW_DIR = "data/raw"
REPORTS_DIR = "data/reports"

# Headers padrão para scraping
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}
""