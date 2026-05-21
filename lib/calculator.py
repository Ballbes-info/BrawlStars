"""
Калькулятор "Что если?" — считает PSI без API.
Чистая математика на основе текущего PSI.
"""
from .psi_calculator import PRESTIGE_BASE, RANKED_POINTS
import json, os


def load_tiers():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_p2_boost(brawlers: list, count: int = 5) -> dict:
    """
    Сколько PSI даст если поднять N бравлеров до P2 (2000 трофеев).
    Выбирает самых выгодных (F-Tier > D-Tier > ...).
    """
    tiers_data = load_tiers()
    current_psi = 60.5  # заглушка, будет передаваться

    # Находим бравлеров с трофеями < 2000, сортируем по выгодности
    candidates = []
    for b in brawlers:
        trophies = b.get("trophies", 0)
        if trophies < 2000:
            name = b.get("name", "").upper()
            tier = tiers_data.get(name, {}).get("tier", "B")
            # Сколько PSI даст P2 этого бравлера
            p2_score = PRESTIGE_BASE[2][tier]
            p1_score = PRESTIGE_BASE[1][tier] if trophies >= 1000 else 0
            boost = p2_score - p1_score
            candidates.append({
                "name": b.get("name"),
                "tier": tier,
                "trophies": trophies,
                "boost": boost
            })

    # Сортируем по выгодности
    candidates.sort(key=lambda x: x["boost"], reverse=True)
    top = candidates[:count]

    total_boost = sum(c["boost"] for c in top)
    new_psi = current_psi + total_boost

    return {
        "count": len(top),
        "total_boost": round(total_boost, 1),
        "new_psi": round(new_psi, 1),
        "brawlers": [{"name": c["name"], "tier": c["tier"], "boost": round(c["boost"], 1)} for c in top]
    }


def calc_rank_boost(current_rank: str, target_rank: str) -> dict:
    """
    Сколько PSI даст если поднять ранг.
    """
    current_score = 0
    target_score = 0

    for key, points in RANKED_POINTS.items():
        if key in current_rank.upper():
            current_score = points
        if key in target_rank.upper():
            target_score = points

    boost = target_score - current_score
    return {
        "current_rank": current_rank,
        "target_rank": target_rank,
        "current_score": current_score,
        "target_score": target_score,
        "boost": boost
    }


def calc_top200_boost(brawler_count: int = 3) -> dict:
    """
    Сколько PSI даст если попасть в топ-200 по N бравлерам.
    """
    boost_per_brawler = 3  # за каждого в топ-200 мира
    total_boost = min(9, brawler_count * boost_per_brawler)
    return {
        "brawler_count": brawler_count,
        "boost_per_brawler": boost_per_brawler,
        "total_boost": total_boost
    }


def calc_max_boost(brawlers: list, current_rank: str) -> dict:
    """
    Максимальный буст PSI.
    """
    p2 = calc_p2_boost(brawlers, 10)
    rank = calc_rank_boost(current_rank, "PRO")
    top200 = calc_top200_boost(3)

    total = p2["total_boost"] + rank["boost"] + top200["total_boost"]

    return {
        "p2_boost": p2,
        "rank_boost": rank,
        "top200_boost": top200,
        "total_possible_boost": round(total, 1)
    }