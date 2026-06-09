import os
import sys
import argparse
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import ANALYSIS_CONFIG, REPORTS_DIR
from agents.trend_analyzer import TrendAnalyzer
from agents.product_analyzer import ProductAnalyzer
from agents.price_scraper import PriceScraper
from agents.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Agente de análise de tendências de moda e vendas")
    parser.add_argument("--keywords", nargs="*", help="Palavras-chave customizadas para busca")
    parser.add_argument("--platforms", nargs="*", default=None,
                        help="Plataformas para buscar (mercado_livre, shopee, instagram, etc)")
    parser.add_argument("--limit", type=int, default=20, help="Limite de produtos no relatório")
    parser.add_argument("--days", type=int, default=30, help="Janela de tempo para tendências (dias)")
    parser.add_argument("--output", type=str, default=None, help="Nome do arquivo de relatório")
    args = parser.parse_args()

    print("🚀 Iniciando Moda Agent")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Configurar keywords
    keywords = args.keywords if args.keywords else ANALYSIS_CONFIG["trend_keywords"]
    print(f"🔍 Keywords: {', '.join(keywords[:5])}{', ...' if len(keywords) > 5 else ''}")

    # 1. Buscar tendências
    ta = TrendAnalyzer(keywords=keywords, platforms=args.platforms)
    trend_data = ta.run()

    # 2. Coletar produtos e preços
    ps = PriceScraper(platforms=args.platforms)
    product_data = ps.run(keywords, limit=args.limit)

    # 3. Analisar produtos
    pa = ProductAnalyzer()
    analysis_results = pa.run(trend_data, product_data, days=args.days)

    # 4. Gerar relatório
    rg = ReportGenerator()
    output_file = args.output or f"relatorio_moda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    report_path = os.path.join(REPORTS_DIR, output_file)

    rg.generate_report(
        analysis_results,
        output_path=report_path,
        summary=f"Relatório de tendências de moda — {datetime.now().strftime('%d/%m/%Y')}
    )

    print(f"✅ Relatório gerado em: {report_path}")
    print("\nPrincipais insights:")
    for insight in analysis_results.get("insights", [])[:3]:
        print(f"- {insight}")


if __name__ == "__main__":
    main()
