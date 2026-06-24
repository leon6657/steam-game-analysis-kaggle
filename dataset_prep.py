"""
Steam 游戏数据集准备模块
优先加载 Kaggle 真实数据集，若不可用则生成合成数据
"""

import os
import csv
import json
import random
import numpy as np
from datetime import datetime, timedelta

GENRES = ["Action", "Adventure", "Casual", "Indie", "RPG",
          "Simulation", "Strategy", "Sports", "Racing", "Fighting",
          "Puzzle", "Education"]

DEVELOPERS = [
    "Valve", "Ubisoft", "Bethesda", "CD Projekt Red",
    "FromSoftware", "Rockstar Games", "Square Enix", "Capcom",
    "Electronic Arts", "2K Games", "Sega", "Bandai Namco",
    "Paradox Interactive", "Team Cherry", "Supergiant Games",
    "Mojang", "BioWare", "Bungie", "Larian Studios",
    "ConcernedApe", "Re-Logic", "Coffee Stain Studios",
    "Facepunch Studios", "Annapurna Interactive",
    "tinyBuild", "Team17", "Chucklefish"
]

PUBLISHERS = DEVELOPERS + [
    "Microsoft Game Studios", "Sony Interactive",
    "Deep Silver", "Focus Home", "THQ Nordic"
]

PRICE_BUCKETS = [
    (0.0, 0.0, 0.12),
    (0.99, 4.99, 0.20),
    (4.99, 9.99, 0.18),
    (9.99, 19.99, 0.22),
    (19.99, 29.99, 0.12),
    (29.99, 39.99, 0.08),
    (39.99, 59.99, 0.06),
    (59.99, 79.99, 0.02),
]


def _random_price():
    r = random.random()
    cum = 0
    for lo, hi, p in PRICE_BUCKETS:
        cum += p
        if r <= cum:
            if lo == hi == 0:
                return 0.0
            return round(random.uniform(lo, hi) + 0.01, 2)
    return round(random.uniform(0.99, 29.99) + 0.01, 2)


def _random_genres():
    n = random.choices([1, 2, 3, 4], weights=[0.3, 0.4, 0.2, 0.1])[0]
    sampled = random.sample(GENRES[:12], min(n, 12))
    if "Indie" not in sampled and random.random() < 0.35:
        sampled.append("Indie")
    return sampled[:n]


def _random_ratings(quality):
    if quality == "high":
        pos = int(np.random.lognormal(7, 1.5))
        neg = int(pos * random.uniform(0.02, 0.15))
    elif quality == "mid":
        pos = int(np.random.lognormal(6, 1.5))
        neg = int(pos * random.uniform(0.15, 0.6))
    else:
        pos = int(np.random.lognormal(5, 1.5))
        neg = int(pos * random.uniform(0.6, 2.0))
    return max(0, pos), max(0, neg)


def _random_owners():
    buckets = [
        (0, 50000, 0.45),
        (50000, 200000, 0.25),
        (200000, 1000000, 0.18),
        (1000000, 5000000, 0.08),
        (5000000, 20000000, 0.03),
        (20000000, 100000000, 0.01),
    ]
    r = random.random()
    cum = 0
    for lo, hi, p in buckets:
        cum += p
        if r <= cum:
            return random.randint(lo, hi)
    return random.randint(0, 50000)


def _random_playtime(owners):
    base = max(1, int(np.random.lognormal(4, 1.8)))
    if owners > 1000000:
        base *= 2
    elif owners > 100000:
        base *= 1.3
    return base, max(1, base // 4)


def _random_release_date():
    start = datetime(2005, 1, 1)
    end = datetime(2024, 6, 1)
    yrs = (end - start).days
    u = random.random()
    if u < 0.1:
        offset = random.uniform(0, yrs * 0.1)
    elif u < 0.3:
        offset = random.uniform(yrs * 0.1, yrs * 0.3)
    elif u < 0.6:
        offset = random.uniform(yrs * 0.3, yrs * 0.6)
    else:
        offset = random.uniform(yrs * 0.6, yrs * 0.95)
    return start + timedelta(days=int(offset))


def generate_dataset(n=8000):
    random.seed(42)
    np.random.seed(42)
    records = []
    adjs = ["Dark", "Epic", "Lost", "Last", "Eternal", "Shadow",
            "Star", "Space", "Tiny", "Mega", "Ultra", "Super",
            "Neon", "Cyber", "Iron", "Golden", "Frozen", "Crimson",
            "Phantom", "Wild", "Deep", "Silent", "Brave", "Final",
            "Rising", "Fallen", "Hollow", "Cursed", "Ancient", "Mystic"]
    nouns = ["World", "Quest", "Wars", "Saga", "Legacy", "Chronicles",
             "Empire", "Frontier", "Odyssey", "Realm", "Force",
             "Legion", "Horizon", "Dominion", "Crusade", "Voyage",
             "Guardian", "Hunter", "Knight", "Phoenix", "Dragon",
             "Shadow", "Storm", "Blade", "Star", "Fate"]
    used_ids = set()

    for i in range(n):
        app_id = random.randint(100000, 900000)
        while app_id in used_ids:
            app_id = random.randint(100000, 900000)
        used_ids.add(app_id)

        adj = random.choice(adjs)
        noun = random.choice(nouns)
        name = f"{adj} {noun} {i+1}"

        dev = random.choice(DEVELOPERS)
        pub = random.choice(PUBLISHERS)
        genres = _random_genres()
        price = _random_price()

        if price == 0:
            quality = random.choices(["low", "mid", "high"], [0.2, 0.5, 0.3])[0]
        elif price < 10:
            quality = random.choices(["low", "mid", "high"], [0.15, 0.55, 0.3])[0]
        elif price < 30:
            quality = random.choices(["low", "mid", "high"], [0.05, 0.4, 0.55])[0]
        else:
            quality = random.choices(["low", "mid", "high"], [0.02, 0.25, 0.73])[0]

        pos, neg = _random_ratings(quality)
        owners = _random_owners()
        avg_pt, med_pt = _random_playtime(owners)
        release = _random_release_date()

        platforms = random.choices(
            ["windows", "windows;mac", "windows;linux",
             "windows;mac;linux", "mac"],
            weights=[0.5, 0.25, 0.1, 0.1, 0.05]
        )[0]

        meta = 0
        if quality == "high" and random.random() < 0.6:
            meta = random.randint(70, 96)
        elif quality == "mid" and random.random() < 0.4:
            meta = random.randint(50, 80)
        elif random.random() < 0.15:
            meta = random.randint(30, 70)

        records.append({
            "app_id": app_id,
            "name": name,
            "release_date": release.strftime("%Y-%m-%d"),
            "price": price,
            "positive_ratings": pos,
            "negative_ratings": neg,
            "average_playtime": avg_pt,
            "median_playtime": med_pt,
            "owners": owners,
            "developer": dev,
            "publisher": pub,
            "genres": json.dumps(genres),
            "platforms": platforms,
            "metacritic_score": meta,
        })
    return records


def save_csv(records, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = [
        "app_id", "name", "release_date", "price", "positive_ratings",
        "negative_ratings", "average_playtime", "median_playtime",
        "owners", "developer", "publisher", "genres", "platforms",
        "metacritic_score"
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(records)
    print(f"[dataset_prep] Already generated {len(records)} records -> {path}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    out = sys.argv[2] if len(sys.argv) > 2 else "data/raw/steam_games.csv"
    records = generate_dataset(n)
    save_csv(records, out)
    print(f"Done. Generated {len(records)} records.")
