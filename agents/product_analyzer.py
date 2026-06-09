""import pandas as pd
import numpy as np
from typing import Dict, List, Any
from config import ANALYSIS_CONFIG
from utils.helpers import calculate_competitiveness_score, moving_average


class ProductAnalyzer:
    def __init__(self):
        pass

    def run(self, trend_data: Dict[str, Any], product_data: Dict[str, List[Dict]], days: int = 30) -> Dict[str, Any]:
        """Analisa produtos coletados e gera ranking de melhores oportunidades."""
        print("📊 Analisando e ranqueando produtos...")

        # Converter tudo em um DataFrame único
        df = self._build_dataframe(product_data)
        if df.empty:
            return {"error": "Nenhum produto encontrado para analisar."}

        # Calcular métricas
        df = self._calculate_metrics(df, trend_data, days)

        # Classificar: score composto
        df = df.sort_values(["trend_score", "competitiveness", "rating"], ascending=[False, False, False])

        # Gerar insights
        insights = self._generate_insights(df, trend_data)

        # Top produtos por categoria
        top_by_cat = {}
        for cat in df["category"].unique():
            cat_df = df[df["category"] == cat].head(5)
            top_by_cat[cat] = cat_df.to_dict('records')

        return {
            "total_products_analyzed": len(df),
            "top_products": df.head(ANALYSIS_CONFIG["top_products_limit"]).to_dict('records'),
            "top_by_category": top_by_cat,
            "price_stats": self._get_price_stats(df),
            "insights": insights,
            "analysis_window_days": days,
            "timestamp": pd.Timestamp.now().isoformat()
        }

    def _build_dataframe(self, product_data: Dict[str, List[Dict]]) -> pd.DataFrame:
        rows = []
        for platform, products in product_data.items():
            for p in products:
                row = p.copy()
                row["platform"] = platform
                row["price_num"] = float(row.get("price", 0) or 0)
                row["rating_num"] = float(row.get("rating", 0) or 0)
                row["sales_num"] = int(row.get("sales", 0) or 0)
                row["category"] = row.get("category") or "Não classificado"
                rows.append(row)
        df = pd.DataFrame(rows)
        return df if not df.empty else pd.DataFrame(columns=["title","price_num","rating_num","sales_num","platform","url","category"])

    def _calculate_metrics(self, df: pd.DataFrame, trend_data: Dict[str, Any], days: int) -> pd.DataFrame:
        # Score de tendência (0-1): presença nas tendências emergentes
        themes = set([t.lower() for t in trend_data.get("emerging_themes", [])])
        df["trend_score"] = df["title"].apply(lambda x: self._title_theme_match(x, themes))

        # Score de competitividade (0-1): preço relativo ao mercado
        df["competitiveness"] = df.apply(lambda row: calculate_competitiveness_score(row, df), axis=1)

        # Score de qualidade: rating * (sales / max_sales)
        max_sales = df["sales_num"].max() or 1
        df["quality_score"] = (df["rating_num"] / 5.0) * (df["sales_num"] / max_sales) if max_sales > 0 else 0

        # Score final composto
        df["final_score"] = (
            0.4 * df["trend_score"] +
            0.3 * df["competitiveness"] +
            0.3 * df["quality_score"]
        )

        return df

    def _title_theme_match(self, title: str, themes: set) -> float:
        if not themes or not title:
            return 0.0
        title_lower = title.lower()
        score = 0.0
        for theme in themes:
            if theme and any(kw in title_lower for kw in [theme.lower()]):
                score += 1.0
        return min(score / len(themes), 1.0)

    def _get_price_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {}
        return {
            "mean": float(df["price_num"].mean()),
            "median": float(df["price_num"].median()),
            "min": float(df["price_num"].min()),
            "max": float(df["price_num"].max()),
            "std": float(df["price_num"].std()),
            "by_category": df.groupby("category")["price_num"].agg(["mean","median","count"]).to_dict('index')
        }

    def _generate_insights(self, df: pd.DataFrame, trend_data: Dict[str, Any]) -> List[str]:
        insights = []

        if not df.empty:
            top = df.head(10)
            # Categoria mais promissora
            top_cat = top["category"].value_counts().idxmax()
            insights.append(f"Categoria com maior potencial: **{top_cat}**")

            # Faixa de preço ideal
            cat_mean = df[df["category"] == top_cat]["price_num"].mean() if top_cat else 0
            insights.append(f"Faixa de preço ideal na categoria {top_cat}: R$ {cat_mean*0.8:.0f} - R$ {cat_mean*1.2:.0f}")

            # Plataforma com mais oportunidades
            best_platform = top["platform"].value_counts().idxmax()
            insights.append(f"Plataforma com mais produtos promissores: **{best_platform}**")

            # Temas emergentes relevantes
            themes = trend_data.get("emerging_themes", [])
            if themes:
                insights.append(f"Temas emergentes a explorar: {', '.join(themes[:3])}")

        else:
            insights.append("Nenhum produto suficiente para gerar insights. Tente ampliar as palavras-chave ou plataformas.")

        return insights
""