"""
数据管道：加载 -> 清洗 -> 存储 SQLite
"""

import json
import os
import sqlite3
import pandas as pd
import numpy as np


def load_dataset(path):
    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    print(f"[data_pipeline] 加载 {len(df)} 条记录")

    # 自动检测数据集格式
    cols = set(df.columns)
    if "metacritic_score" in cols:
        print("[data_pipeline] 检测到: 合成数据集格式")
    elif "categories" in cols or "steamspy_tags" in cols:
        print("[data_pipeline] 检测到: Kaggle 数据集格式")
        # 字段名映射 (Kaggle -> 统一格式)
        rename = {
            "app_id": "app_id", "name": "name", "release_date": "release_date",
            "price": "price", "developer": "developer", "publisher": "publisher",
            "positive_ratings": "positive_ratings", "negative_ratings": "negative_ratings",
            "average_playtime": "average_playtime", "median_playtime": "median_playtime",
            "owners": "owners", "genres": "genres",
        }
        # 部分 Kaggle 版本用 platforms 或 platform
        if "platforms" in cols:
            rename["platforms"] = "platforms"
        elif "platform" in cols:
            rename["platform"] = "platforms"
        # 只保留需要的列
        keep = {v: k for k, v in rename.items() if k in cols}
        df = df[list(keep.keys())].rename(columns=keep)
        # 补充分类字段
        df["metacritic_score"] = 0
    else:
        print("[data_pipeline] 未知格式，尝试兼容加载...")

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    for col in ["price", "positive_ratings", "negative_ratings",
                 "average_playtime", "median_playtime", "owners",
                 "metacritic_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_data(df):
    before = len(df)
    df = df.drop_duplicates(subset=["app_id"])
    df = df.drop_duplicates(subset=["name"])
    df = df.dropna(subset=["name", "release_date"])
    df = df[(df["price"] >= 0) & (df["price"] <= 200)]
    df["positive_ratings"] = df["positive_ratings"].clip(0, 1_000_000)
    df["negative_ratings"] = df["negative_ratings"].clip(0, 1_000_000)
    df["release_year"] = df["release_date"].dt.year
    df = df.dropna(subset=["release_year"])
    df["release_year"] = df["release_year"].astype(int)
    total = df["positive_ratings"] + df["negative_ratings"]
    df["rating_score"] = (df["positive_ratings"] / total.replace(0, np.nan) * 100).round(1)

    def parse_genres(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            try:
                return json.loads(x)
            except (json.JSONDecodeError, TypeError):
                return [g.strip() for g in x.split(",") if g.strip()]
        return []

    df["genres_list"] = df["genres"].apply(parse_genres)
    after = len(df)
    print(f"[data_pipeline] 清洗: {before} -> {after} 条")
    return df


def store_data(df, db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cols = ["app_id", "name", "release_date", "release_year",
            "price", "positive_ratings", "negative_ratings", "rating_score",
            "average_playtime", "median_playtime", "owners",
            "developer", "publisher", "genres", "platforms",
            "metacritic_score"]
    store = df[cols].copy()
    store["release_date"] = store["release_date"].dt.strftime("%Y-%m-%d")
    store.to_sql("steam_games", conn, if_exists="replace", index=False)
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_developer ON steam_games(developer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_year ON steam_games(release_year)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_price ON steam_games(price)")
    conn.commit()
    conn.close()
    print(f"[data_pipeline] 已写入 {len(store)} 条到 {db_path}")


def run_pipeline(csv_path, db_path):
    df = load_dataset(csv_path)
    df = clean_data(df)
    store_data(df, db_path)
    return df


if __name__ == "__main__":
    run_pipeline("data/raw/steam_games.csv", "data/processed/steam.db")
