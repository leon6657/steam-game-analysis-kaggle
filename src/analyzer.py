"""
分析引擎：6 大分析模块
"""

import json
import pandas as pd
import numpy as np
import json as _json


class SteamAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.genre_rows = []
        for _, row in self.df.iterrows():
            raw = row.get("genres_list", None)
            if raw is None:
                raw = row.get("genres", "[]")
            if isinstance(raw, str):
                try:
                    gl = _json.loads(raw)
                except Exception:
                    gl = [g.strip() for g in raw.split(",") if g.strip()]
            elif isinstance(raw, list):
                gl = raw
            else:
                gl = []
            if not gl:
                gl = ["Other"]
            for g in gl:
                self.genre_rows.append({**row.to_dict(), "genre": g})
        self.genre_df = pd.DataFrame(self.genre_rows)

    # ---- 1. 市场总览 ----
    def market_overview(self):
        df = self.df
        free_count = int((df["price"] == 0).sum())
        paid_count = int((df["price"] > 0).sum())
        avg_price = round(df[df["price"] > 0]["price"].mean(), 2)
        total_pos = int(df["positive_ratings"].sum())
        total_neg = int(df["negative_ratings"].sum())
        total_ratings = total_pos + total_neg
        overall_pos_rate = round(total_pos / total_ratings * 100, 1) if total_ratings else 0
        genre_counts = self.genre_df.groupby("genre").size().reset_index(name="count")
        genre_counts = genre_counts.sort_values("count", ascending=False).head(15)
        year_counts = df.groupby("release_year").size().reset_index(name="count")
        year_counts = year_counts.sort_values("release_year")
        return {
            "total_games": int(len(df)),
            "free_games": free_count,
            "paid_games": paid_count,
            "avg_price": avg_price,
            "total_positive": total_pos,
            "total_negative": total_neg,
            "overall_pos_rate": overall_pos_rate,
            "total_ratings": total_ratings,
            "genre_distribution": genre_counts.to_dict("records"),
            "yearly_releases": year_counts.to_dict("records"),
            "avg_playtime": round(df["average_playtime"].mean(), 0),
        }

    # ---- 2. 价格分析 ----
    def price_analysis(self):
        df = self.df
        bins = [0, 0.99, 4.99, 9.99, 14.99, 19.99, 29.99, 39.99, 59.99, 200]
        labels = ["免费", "$0.99-4.99", "$5-9.99", "$10-14.99",
                  "$15-19.99", "$20-29.99", "$30-39.99", "$40-59.99", "$60+"]
        df["price_range"] = pd.cut(df["price"], bins=bins, labels=labels, right=True)
        price_dist = df.groupby("price_range", observed=True).agg(
            count=("price", "size"),
            avg_rating_score=("rating_score", "mean"),
            avg_owners=("owners", "mean"),
        ).reset_index()
        price_dist.columns = ["range", "count", "avg_rating_score", "avg_owners"]
        free_vs_paid = df.groupby(df["price"] == 0).agg(
            count=("price", "size"),
            avg_rating=("rating_score", "mean"),
            avg_owners=("owners", "mean"),
            avg_playtime=("average_playtime", "mean"),
        ).reset_index()
        free_vs_paid["label"] = free_vs_paid["price"].map({True: "免费", False: "付费"})
        return {
            "price_distribution": price_dist.to_dict("records"),
            "free_vs_paid": free_vs_paid.to_dict("records"),
        }

    # ---- 3. 类型分析 ----
    def genre_analysis(self):
        gdf = self.genre_df
        genre_stats = gdf.groupby("genre").agg(
            count=("app_id", "nunique"),
            avg_price=("price", "mean"),
            avg_rating_score=("rating_score", "mean"),
            avg_owners=("owners", "mean"),
            avg_playtime=("average_playtime", "mean"),
        ).reset_index()
        genre_stats = genre_stats.sort_values("count", ascending=False)
        genre_stats["avg_price"] = genre_stats["avg_price"].round(2)
        genre_stats["avg_rating_score"] = genre_stats["avg_rating_score"].round(1)
        genre_stats["avg_owners"] = genre_stats["avg_owners"].round(0).astype(int)
        genre_stats["avg_playtime"] = genre_stats["avg_playtime"].round(0).astype(int)
        recent = gdf[gdf["release_year"] >= 2014]
        if not recent.empty:
            trend = recent.groupby(["release_year", "genre"]).size().reset_index(name="count")
            top_genres = genre_stats.head(8)["genre"].tolist()
            trend = trend[trend["genre"].isin(top_genres)]
        else:
            trend = pd.DataFrame(columns=["release_year", "genre", "count"])
        return {
            "genre_stats": genre_stats.to_dict("records"),
            "genre_trends": trend.to_dict("records"),
        }

    # ---- 4. 开发商分析 ----
    def developer_analysis(self, top_n=20):
        df = self.df
        dev_stats = df.groupby("developer").agg(
            game_count=("app_id", "nunique"),
            total_positive=("positive_ratings", "sum"),
            total_negative=("negative_ratings", "sum"),
            avg_price=("price", "mean"),
            avg_rating_score=("rating_score", "mean"),
            total_owners=("owners", "sum"),
        ).reset_index()
        dev_stats["total_ratings"] = dev_stats["total_positive"] + dev_stats["total_negative"]
        dev_stats["pos_rate"] = (
            dev_stats["total_positive"] / dev_stats["total_ratings"].replace(0, pd.NA) * 100
        ).round(1)
        dev_stats = dev_stats.sort_values("game_count", ascending=False).head(top_n)
        return {"top_developers": dev_stats.to_dict("records")}

    # ---- 5. 评价分析 ----
    def rating_analysis(self):
        df = self.df
        rating_bins = [0, 20, 40, 60, 70, 80, 90, 100]
        rating_labels = ["0-20", "20-40", "40-60", "60-70", "70-80", "80-90", "90-100"]
        df["rating_bucket"] = pd.cut(df["rating_score"], bins=rating_bins,
                                      labels=rating_labels, right=True)
        rating_dist = df.groupby("rating_bucket", observed=True).size().reset_index(name="count")
        corr_cols = ["price", "positive_ratings", "negative_ratings",
                     "average_playtime", "owners", "metacritic_score", "rating_score"]
        corr_df = df[corr_cols].dropna()
        corr_matrix = corr_df.corr().round(3).reset_index()
        corr_matrix = corr_matrix.rename(columns={"index": "variable"})
        return {
            "rating_distribution": rating_dist.to_dict("records"),
            "correlation_matrix": corr_matrix.to_dict("records"),
            "corr_variables": corr_cols,
        }

    # ---- 6. 发行趋势 ----
    def release_trends(self):
        df = self.df
        year_counts = df.groupby("release_year").size().reset_index(name="total")
        year_counts = year_counts[year_counts["release_year"] >= 2005]
        year_counts = year_counts.sort_values("release_year")

        def platform_bucket(p):
            p = str(p).lower()
            if "win" in p and "mac" in p and "linux" in p:
                return "全平台"
            elif "win" in p and "mac" in p:
                return "Win+Mac"
            elif "win" in p:
                return "仅 Windows"
            return "其他"

        df["platform_group"] = df["platforms"].apply(platform_bucket)
        plat_trend = df[df["release_year"] >= 2010].groupby(
            ["release_year", "platform_group"]).size().reset_index(name="count")
        return {
            "yearly_releases": year_counts.to_dict("records"),
            "platform_trends": plat_trend.to_dict("records"),
        }
