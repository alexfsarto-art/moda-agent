import os

# ========== CONFIGURAÇÕES MARITACA AI ==========
MARITACA_CONFIG = {
    "api_key": os.environ.get("MARITACA_API_KEY", ""),
    "base_url": os.environ.get("MARITACA_BASE_URL", "https://chat.maritaca.ai/api"),
    "model": "sabiazinho-4", 
    "max_tokens": 2000,
    "temperature": 0.7,
    "timeout": 30
}

# Configuração alternativa - OpenAI (se quiser usar como fallback)
OPENAI_CONFIG = {
    "api_key": os.environ.get("OPENAI_API_KEY", ""),
    "model": "gpt-3.5-turbo",
    "max_tokens": 2000,
    "temperature": 0.7
}

# Configuração alternativa - Google Gemini
GEMINI_CONFIG = {
    "api_key": os.environ.get("GEMINI_API_KEY", ""),
    "model": "gemini-pro",
    "temperature": 0.7
}

# Configuração para cache de respostas da IA
AI_CACHE_CONFIG = {
    "enabled": True,
    "ttl_seconds": 3600,  # 1 hora
    "max_size": 100  # Máximo de respostas em cache
}

# Prompts padrão para análise de tendências
DEFAULT_PROMPTS = {
    "trend_analysis": """
    Você é um especialista em tendências de moda. Analise os seguintes dados:
    {data}
    
    Por favor, forneça:
    1. Principais tendências identificadas
    2. Score de tendência (0-100) para cada item
    3. Recomendações para varejistas
    4. Projeção para próximos 3 meses
    """,
    
    "product_ranking": """
    Com base nos seguintes produtos:
    {products}
    
    Ranqueie os produtos considerando:
    - Potencial de venda
    - Alinhamento com tendências
    - Competitividade de preço
    - Qualidade percebida
    
    Retorne um ranking ordenado com scores.
    """,
    
    "insights_generation": """
    Dados analisados:
    {analysis_data}
    
    Gere insights acionáveis para:
    - Estratégia de precificação
    - Mix de produtos
    - Oportunidades de mercado
    """
}

# Configuração de rate limiting para APIs
RATE_LIMIT_CONFIG = {
    "maritaca": {"calls_per_minute": 60, "calls_per_day": 1000},
    "openai": {"calls_per_minute": 60, "calls_per_day": 1000},
    "gemini": {"calls_per_minute": 60, "calls_per_day": 1000}
}
