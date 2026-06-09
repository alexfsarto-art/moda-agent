""# 🛍️ Moda Agent — Agente de Tendências de Moda e Vendas

Agente Python que busca tendências de moda, coleta produtos de e-commerce e gera relatórios analíticos com apoio da API da Maritaca AI.

## 📦 Estrutura
```
moda_agent/
├── main.py                # Entrypoint — executa o fluxo completo
├── .env                   # Variáveis de ambiente (API keys)
├── requirements.txt       # Dependências
├── config.py              # Configurações centralizadas
├── agents/                # Agentes de negócio
│   ├── trend_analyzer.py     # Busca tendências (Google Trends + IA)
│   ├── price_scraper.py      # Coleta produtos/preços (ML, Shopee, Magalu, Amazon)
│   ├── product_analyzer.py   # Ranqueia produtos e gera insights
│   └── report_generator.py   # Gera relatório Excel com gráficos
├── data/
│   ├── raw/               # Dados brutos coletados
│   └── reports/           # Relatórios gerados
└── utils/
    ├── scrapers.py        # Scrapers reutilizáveis
    └── helpers.py          # Funções utilitárias
```

## 🚀 Como usar

### 1. Clonar e instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
Copie `.env.example` para `.env` e adicione sua chave da Maritaca AI:
```bash
cp .env.example .env
# Edite .env e insira sua chave
```

### 3. Executar o agente

**Básico (usa keywords padrão):**
```bash
python main.py
```

**Customizando:**
```bash
python main.py \
  --keywords "vestido verão" "tênis corrida" "bolsa feminina" \
  --platforms mercado_livre shopee \
  --limit 30 \
  --days 60
```

### 4. Onde encontrar o relatório
O relatório é gerado em `data/reports/` no formato Excel (`.xlsx`), com:
- Resumo executivo
- Top produtos ranqueados
- Análise por categoria com gráfico

## ⚙️ Configuração

Editável em `config.py`:
- `ANALYSIS_CONFIG["trend_keywords"]`: lista de keywords padrão
- `ANALYSIS_CONFIG["trend_window_days"]`: janela de tempo para tendências
- `ANALYSIS_CONFIG["top_products_limit"]`: limite de produtos no relatório
- `SEARCH_PLATFORMS`: plataformas disponíveis

## 🧠 Como funciona o fluxo

1. **Trend Analyzer** → busca tendências em Google Trends e Instagram, envia para a Maritava AI para identificar temas emergentes
2. **Price Scraper** → coleta produtos e preços das plataformas configuradas
3. **Product Analyzer** → ranqueia produtos com score composto (tendência + competitividade + qualidade)
4. **Report Generator** → gera Excel com dados, gráficos e insights

## ⚠️ Notas importantes

- Os scrapers de Google Trends e Instagram são **mocks** — em produção, substitua por integrações reais (pytrends, Instagram Graph API).
- Scraping pode violar ToS de algumas plataformas. Use com responsabilidade.
- A API da Maritava AI é usada apenas para análise textual dos dados coletados (não para scraping).
- Para rodar online (ex: Replit, Vercel), certifique-se de que o ambiente permite requests e BeautifulSoup.
""