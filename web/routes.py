"""
Flask 路由 & 数据 API
"""

import json
import sqlite3
import os
import pandas as pd
from flask import Blueprint, render_template, jsonify, request

from src.data_pipeline import load_dataset, clean_data, store_data
from src.analyzer import SteamAnalyzer
from src.visualizer import all_charts

bp = Blueprint("main", __name__)

_analyzer = None
_charts = None
_df = None


def _get_db_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "data", "processed", "steam.db")


def _get_csv_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "data", "raw", "steam_games.csv")


def init_app():
    global _analyzer, _charts, _df
    csv_path = _get_csv_path()
    db_path = _get_db_path()

    if not os.path.exists(csv_path):
        print("[routes] 未找到数据集，正在生成模拟数据...")
        from dataset_prep import generate_dataset, save_csv
        records = generate_dataset(8000)
        save_csv(records, csv_path)

    if os.path.exists(db_path):
        print("[routes] 从 SQLite 加载...")
        conn = sqlite3.connect(db_path)
        _df = pd.read_sql("SELECT * FROM steam_games", conn,
                          parse_dates=["release_date"])
        conn.close()
    else:
        print("[routes] 运行 ETL 管道...")
        _df = load_dataset(csv_path)
        _df = clean_data(_df)
        store_data(_df, db_path)

    _analyzer = SteamAnalyzer(_df)
    _charts = all_charts(_analyzer)
    print(f"[routes] 分析就绪: {len(_df)} 条游戏数据")


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        init_app()
    return _analyzer


def _get_charts():
    global _charts
    if _charts is None:
        init_app()
    return _charts


def _get_df():
    global _df
    if _df is None:
        init_app()
    return _df


# ---------- 页面路由 ----------

@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/games")
def games():
    return render_template("games.html")


@bp.route("/genres")
def genres():
    return render_template("genres.html")


@bp.route("/developers")
def developers():
    return render_template("developers.html")


@bp.route("/price")
def price():
    return render_template("price.html")


# ---------- 数据 API ----------

@bp.route("/api/charts")
def api_charts():
    return jsonify({"success": True, "data": _get_charts()})


@bp.route("/api/overview")
def api_overview():
    return jsonify({"success": True, "data": _get_analyzer().market_overview()})


@bp.route("/api/games")
def api_games():
    df = _get_df()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    search = request.args.get("search", "").strip().lower()
    genre_filter = request.args.get("genre", "").strip()
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["name"].str.lower().str.contains(search, na=False)]
    if genre_filter:
        filtered = filtered[filtered["genres"].str.contains(genre_filter, na=False)]
    if price_min is not None:
        filtered = filtered[filtered["price"] >= price_min]
    if price_max is not None:
        filtered = filtered[filtered["price"] <= price_max]

    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = filtered.iloc[start:end]

    cols = ["app_id", "name", "release_date", "price", "positive_ratings",
            "negative_ratings", "rating_score", "average_playtime",
            "median_playtime", "owners", "developer", "publisher",
            "genres", "platforms", "metacritic_score"]
    cols = [c for c in cols if c in page_data.columns]
    records = page_data[cols].to_dict("records")
    for r in records:
        for k, v in r.items():
            if isinstance(v, (pd.Timestamp,)):
                r[k] = str(v.date())
            elif isinstance(v, float):
                r[k] = round(v, 2)
            elif pd.isna(v):
                r[k] = None

    return jsonify({"success": True, "data": {
        "records": records, "total": total, "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }})


@bp.route("/api/games/<int:app_id>")
def api_game_detail(app_id):
    df = _get_df()
    row = df[df["app_id"] == app_id]
    if row.empty:
        return jsonify({"success": False, "error": "not found"}), 404
    detail = row.iloc[0].to_dict()
    for k, v in detail.items():
        if isinstance(v, (pd.Timestamp,)):
            detail[k] = str(v.date())
        elif isinstance(v, float):
            detail[k] = round(v, 2)
        elif pd.isna(v):
            detail[k] = None
    return jsonify({"success": True, "data": detail})


@bp.route("/api/genres")
def api_genres():
    return jsonify({"success": True, "data": _get_analyzer().genre_analysis()})


@bp.route("/api/developers")
def api_developers():
    top_n = request.args.get("top_n", 20, type=int)
    return jsonify({"success": True,
                    "data": _get_analyzer().developer_analysis(top_n=top_n)})


@bp.route("/api/price")
def api_price():
    return jsonify({"success": True, "data": _get_analyzer().price_analysis()})


@bp.route("/api/ratings")
def api_ratings():
    return jsonify({"success": True, "data": _get_analyzer().rating_analysis()})


@bp.route("/api/trends")
def api_trends():
    return jsonify({"success": True, "data": _get_analyzer().release_trends()})


@bp.route("/api/genre_list")
def api_genre_list():
    df = _get_df()
    all_genres = set()
    for g in df["genres"]:
        if isinstance(g, str):
            try:
                for item in json.loads(g):
                    all_genres.add(item)
            except Exception:
                for item in g.split(","):
                    all_genres.add(item.strip())
        elif isinstance(g, list):
            all_genres.update(g)
    return jsonify({"success": True, "data": sorted(all_genres)})
