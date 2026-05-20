"""
Player Skill Index (PSI) Calculator v2.0.
Рассчитывает скилл игрока по 7 модулям с полной детализацией.
Тиры и классы берутся из data/tiers.json
"""
import json
import os
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# ЗАГРУЗКА ТИРОВ
# ═══════════════════════════════════════════════════════════════════════════════

def _load_tiers() -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════════

PRESTIGE_BASE = {
    1: {"S": 0.5, "A": 0.6, "B": 0.8, "C": 1.1, "D": 1.4, "F": 1.8},
    2: {"S": 1.5, "A": 2.0, "B": 2.5, "C": 3.5, "D": 4.5, "F": 5.5},
    3: {"S": 3.0, "A": 4.0, "B": 5.0, "C": 7.0, "D": 9.0, "F": 11.0},
}

RANKED_POINTS = {
    "BRONZE": 0, "SILVER": 1, "GOLD": 2, "DIAMOND": 4,
    "MYTHIC I": 7, "MYTHIC II": 9, "MYTHIC III": 11,
    "LEGENDARY I": 14, "LEGENDARY II": 17, "LEGENDARY III": 20,
    "MASTER I": 24, "MASTER II": 28, "MASTER III": 32, "PRO": 37,
}

WINRATE_THRESHOLDS = [(80, 10), (70, 8), (65, 6), (60, 4), (55, 2)]
TROPHY_THRESHOLDS = [(100000, 3), (70000, 2), (50000, 1)]
LEVEL_THRESHOLDS = [(700, 3), (500, 2), (300, 1)]
WINSTREAK_THRESHOLDS = [(40, 5), (30, 3), (20, 2)]


# ═══════════════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ
# ═══════════════════════════════════════════════════════════════════════════════

def _norm_tag(t: str) -> str:
    """Нормализация тега: убираем #, O→0, верхний регистр."""
    return t.replace("#", "").replace("O", "0").replace("o", "0").upper()


# ═══════════════════════════════════════════════════════════════════════════════
# МОДУЛЬ 1: ПРАЙМЫ (макс 30)
# ═══════════════════════════════════════════════════════════════════════════════

def calc_module_1(brawlers: list, total_trophies: int) -> dict:
    data = _load_tiers()

    detail = []
    total_score = 0.0
    p1_count = p2_count = p3_count = 0
    d_f_p3_count = 0
    class_p2_set = set()
    tier_counts = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

    for b in brawlers:
        name = b.get("name", "").upper()
        trophies = b.get("trophies", 0)
        info = data.get(name, {})
        tier = info.get("tier", "B")
        b_class = info.get("class", "Unknown")

        prestige = 3 if trophies >= 3000 else 2 if trophies >= 2000 else 1 if trophies >= 1000 else 0

        if prestige == 0:
            continue

        score = PRESTIGE_BASE[prestige][tier]
        total_score += score
        tier_counts[tier] += 1

        if prestige == 1:
            p1_count += 1
        elif prestige == 2:
            p1_count += 1
            p2_count += 1
        elif prestige == 3:
            p1_count += 1
            p2_count += 1
            p3_count += 1

        if prestige >= 2:
            class_p2_set.add(b_class)

        if prestige >= 3 and tier in ("D", "F"):
            d_f_p3_count += 1

    detail.append(f"  P1: {p1_count} бойцов | P2: {p2_count} | P3: {p3_count}")
    detail.append(
        f"  S: {tier_counts['S']} | A: {tier_counts['A']} | B: {tier_counts['B']} | C: {tier_counts['C']} | D: {tier_counts['D']} | F: {tier_counts['F']}")
    detail.append(f"  База праймов: {total_score:.2f} баллов")

    # Бонус плотности всех праймов (P1+P2+P3)
    total_brawlers = len(brawlers)
    all_density = (p1_count + p2_count + p3_count) / max(1, total_brawlers)
    bonus_all_density = 0
    if all_density > 0.5:
        bonus_all_density = 2
    elif all_density > 0.3:
        bonus_all_density = 1
    detail.append(
        f"  Бонус плотности (P1+P2+P3): {bonus_all_density} (плотность {all_density:.3f} = {p1_count + p2_count + p3_count}/{total_brawlers})")

    # Бонус плотности высших праймов (P2+P3)
    high_density = (p2_count + p3_count) / max(1, total_brawlers)
    bonus_high_density = 0
    if high_density > 0.3:
        bonus_high_density = 3
    elif high_density > 0.15:
        bonus_high_density = 2
    elif high_density > 0.05:
        bonus_high_density = 1
    detail.append(
        f"  Бонус плотности (P2+P3): {bonus_high_density} (плотность {high_density:.3f} = {p2_count + p3_count}/{total_brawlers})")

    # Бонус разнообразия
    bonus_diversity = 2 if len(class_p2_set) >= 5 else 0
    detail.append(
        f"  Бонус разнообразия: {bonus_diversity} (P2+ в {len(class_p2_set)} классах: {', '.join(sorted(class_p2_set)) if class_p2_set else 'нет'})")

    # Бонус количества
    if p3_count >= 50:
        bonus_count = 4
    elif p3_count >= 25:
        bonus_count = 2
    else:
        bonus_count = 0
    detail.append(f"  Бонус количества праймов: {bonus_count} (P3: {p3_count})")

    # Бонус D/F P3
    bonus_df = min(5, d_f_p3_count)
    detail.append(f"  Бонус D/F P3: {bonus_df} (бойцов: {d_f_p3_count})")

    result = total_score + bonus_all_density + bonus_high_density + bonus_diversity + bonus_count + bonus_df
    result = min(30, result)
    detail.append(f"  ИТОГО модуль 1: {result:.2f}/30")

    return {"score": result, "detail": detail}


# ═══════════════════════════════════════════════════════════════════════════════
# МОДУЛЬ 2: RANKED (макс 37)
# ═══════════════════════════════════════════════════════════════════════════════

def calc_module_2(player_data: dict) -> dict:
    rank_name = player_data.get("highestAllTimeRankedRankName", "?")
    current_rank = player_data.get("rankedRankName", "?")
    current_elo = player_data.get("rankedElo", 0)
    best_elo = player_data.get("highestAllTimeRankedElo", 0)

    score = 0.0
    for key, points in RANKED_POINTS.items():
        if key in rank_name.upper():
            score = float(points)
            break

    detail = [
        f"  Текущий ранг: {current_rank} (ELO: {current_elo})",
        f"  Лучший за всё время: {rank_name} (ELO: {best_elo})",
        f"  ИТОГО модуль 2: {score:.2f}/37",
    ]
    return {"score": score, "detail": detail}


# ═══════════════════════════════════════════════════════════════════════════════
# МОДУЛЬ 3: ТОП-МИР + ТОП-РЕГИОН (макс 20)
# ═══════════════════════════════════════════════════════════════════════════════

def calc_module_3(player_data: dict, brawlers: list, api: Any, tag: str) -> dict:
    detail = []
    result = 0.0

    # 3a. Старые ранги 35
    r35_count = sum(1 for b in brawlers if b.get("rank", 0) >= 35)
    r35_score = 0
    if r35_count >= 10:
        r35_score = 10
    elif r35_count >= 5:
        r35_score = 8
    elif r35_count >= 3:
        r35_score = 5
    elif r35_count >= 1:
        r35_score = 2
    result += r35_score
    detail.append(f"  Старые ранги 35: {r35_count} шт → {r35_score} баллов")

    # 3b. Топ мира общий — сравнение с 200-м местом
    world_score = 0
    player_trophies = player_data.get("trophies", 0)
    try:
        rankings = api.get_player_rankings("global", limit=200)
        items = rankings.get("items", [])
        if items:
            last_trophies = items[-1].get("trophies", 0)
            if player_trophies >= last_trophies:
                if len(items) >= 50:
                    top50_trophies = items[49].get("trophies", 0)
                    world_score = 10 if player_trophies >= top50_trophies else 6
                else:
                    world_score = 6
                detail.append(f"  Топ мира общий: входит → {world_score} баллов")
        if world_score == 0:
            detail.append("  Топ мира общий: не входит → 0 баллов")
    except Exception:
        detail.append("  Топ мира общий: ошибка → 0 баллов")
    result += world_score

    # 3c. Топ России общий — сравнение с 200-м местом
    ru_score = 0
    try:
        rankings = api.get_player_rankings("ru", limit=200)
        items = rankings.get("items", [])
        if items and player_trophies >= items[-1].get("trophies", 0):
            ru_score = 3
            detail.append(f"  Топ России общий: входит → {ru_score} баллов")
    except Exception:
        pass
    result += ru_score

    # 3d. Топ бравлеров — сравнение с 200-м местом
    top_brawler_world = []
    top_brawler_ru = []
    found_world = True
    found_ru = True

    for b in sorted(brawlers, key=lambda x: x.get("trophies", 0), reverse=True):
        if not found_world and not found_ru:
            break
        b_id = b.get("id")
        b_name = b.get("name", "?")
        b_trophies = b.get("trophies", 0)
        if b_trophies < 500:
            break

        if found_world:
            try:
                rankings = api.get_brawler_rankings("global", b_id, limit=200)
                items = rankings.get("items", [])
                if items and b_trophies >= items[-1].get("trophies", 0):
                    top_brawler_world.append((b_name, b_trophies))
                else:
                    found_world = False
            except Exception:
                found_world = False

        if found_ru:
            try:
                rankings = api.get_brawler_rankings("ru", b_id, limit=200)
                items = rankings.get("items", [])
                if items and b_trophies >= items[-1].get("trophies", 0):
                    top_brawler_ru.append((b_name, b_trophies))
                else:
                    found_ru = False
            except Exception:
                found_ru = False

    brawler_world_score = min(9, len(top_brawler_world) * 3)
    brawler_ru_score = min(6, len(top_brawler_ru) * 2)

    if top_brawler_world:
        detail.append(f"  Топ мира по бравлерам: {len(top_brawler_world)} шт → {brawler_world_score} баллов")
        for name, troph in top_brawler_world:
            detail.append(f"    - {name}: {troph} трофеев")
    else:
        detail.append("  Топ мира по бравлерам: нет → 0 баллов")

    if top_brawler_ru:
        detail.append(f"  Топ России по бравлерам: {len(top_brawler_ru)} шт → {brawler_ru_score} баллов")
        for name, troph in top_brawler_ru:
            detail.append(f"    - {name}: {troph} трофеев")
    else:
        detail.append("  Топ России по бравлерам: нет → 0 баллов")

    result += brawler_world_score + brawler_ru_score
    result = min(20, result)
    detail.append(f"  ИТОГО модуль 3: {result:.2f}/20")

    return {"score": result, "detail": detail}


# ═══════════════════════════════════════════════════════════════════════════════
# МОДУЛЬ 4: ВЕТЕРАН (макс 8)
# ═══════════════════════════════════════════════════════════════════════════════

def calc_module_4(brawlers: list) -> dict:
    r35_count = sum(1 for b in brawlers if b.get("rank", 0) >= 35)
    if r35_count >= 10:
        score = 8
    elif r35_count >= 5:
        score = 6
    elif r35_count >= 3:
        score = 4
    elif r35_count >= 1:
        score = 2
    else:
        score = 0

    detail = [
        f"  Старые ранги 35: {r35_count} шт",
        f"  ИТОГО модуль 4: {score:.2f}/8",
    ]
    return {"score": score, "detail": detail}


# ═══════════════════════════════════════════════════════════════════════════════
# МОДУЛЬ 5: КОЛИЧЕСТВЕННЫЕ (макс 15)
# ═══════════════════════════════════════════════════════════════════════════════

def calc_module_5(player_data: dict, brawlers: list) -> dict:
    detail = []
    result = 0.0

    victories_3v3 = player_data.get("3vs3Victories", 0)
    solo = player_data.get("soloVictories", 0)
    duo = player_data.get("duoVictories", 0)
    total_battles = victories_3v3 + solo + duo
    wr_score = 0
    winrate = 0
    if total_battles > 0:
        winrate = (victories_3v3 / total_battles) * 100
        for threshold, points in WINRATE_THRESHOLDS:
            if winrate >= threshold:
                wr_score = points
                break
        detail.append(f"  Винрейт 3v3: {winrate:.1f}% → {wr_score} баллов")
    else:
        detail.append("  Винрейт 3v3: нет данных → 0 баллов")
    result += wr_score

    p1_count = sum(1 for b in brawlers if b.get("trophies", 0) >= 1000)
    p2_count = sum(1 for b in brawlers if b.get("trophies", 0) >= 2000)
    p3_count = sum(1 for b in brawlers if b.get("trophies", 0) >= 3000)
    total_brawlers = len(brawlers)

    all_density = (p1_count + p2_count + p3_count) / max(1, total_brawlers)
    high_density = (p2_count + p3_count) / max(1, total_brawlers)

    density_score = 0
    if high_density > 0.3:
        density_score = 3
    elif high_density > 0.15:
        density_score = 2
    elif all_density > 0.3:
        density_score = 1

    detail.append(
        f"  Плотность праймов: все {all_density:.3f} ({p1_count + p2_count + p3_count}/{total_brawlers}), высшие {high_density:.3f} ({p2_count + p3_count}/{total_brawlers}) → {density_score} баллов")
    result += density_score

    total_trophies = player_data.get("trophies", 0)
    trophy_score = 0
    for threshold, points in TROPHY_THRESHOLDS:
        if total_trophies >= threshold:
            trophy_score = points
            break
    detail.append(f"  Трофеи: {total_trophies} → {trophy_score} баллов")
    result += trophy_score

    exp_level = player_data.get("expLevel", 0)
    level_score = 0
    for threshold, points in LEVEL_THRESHOLDS:
        if exp_level >= threshold:
            level_score = points
            break
    detail.append(f"  Уровень: {exp_level} → {level_score} баллов")
    result += level_score

    result = min(15, result)
    detail.append(f"  ИТОГО модуль 5: {result:.2f}/15")
    return {"score": result, "detail": detail}


# ═══════════════════════════════════════════════════════════════════════════════
# МОДУЛЬ 6: КАЧЕСТВЕННЫЕ (макс 10)
# ═══════════════════════════════════════════════════════════════════════════════

def calc_module_6(brawlers: list) -> dict:
    data = _load_tiers()
    detail = []
    result = 0.0

    max_streak = max((b.get("maxWinStreak", 0) for b in brawlers), default=0)
    streak_score = 0
    for threshold, points in WINSTREAK_THRESHOLDS:
        if max_streak >= threshold:
            streak_score = points
            break
    detail.append(f"  Макс. серия побед: {max_streak} → {streak_score} баллов")
    result += streak_score

    d_f_p3 = []
    for b in brawlers:
        if b.get("trophies", 0) >= 3000:
            name = b.get("name", "").upper()
            tier = data.get(name, {}).get("tier", "B")
            if tier in ("D", "F"):
                d_f_p3.append(b.get("name", ""))
    df_score = min(6, len(d_f_p3) * 2)
    detail.append(f"  D/F P3: {len(d_f_p3)} бойцов ({', '.join(d_f_p3) if d_f_p3 else 'нет'}) → {df_score} баллов")
    result += df_score

    class_p2_set = set()
    for b in brawlers:
        if b.get("trophies", 0) >= 2000:
            name = b.get("name", "").upper()
            b_class = data.get(name, {}).get("class", "Unknown")
            class_p2_set.add(b_class)
    uni_score = 2 if len(class_p2_set) >= 4 else 0
    detail.append(f"  Универсальность: P2+ в {len(class_p2_set)} классах → {uni_score} баллов")
    result += uni_score

    result = min(10, result)
    detail.append(f"  ИТОГО модуль 6: {result:.2f}/10")
    return {"score": result, "detail": detail}


# ═══════════════════════════════════════════════════════════════════════════════
# МОДУЛЬ 7: КЛУБ (макс 0.5)
# ═══════════════════════════════════════════════════════════════════════════════

def calc_module_7(player_data: dict) -> dict:
    club = player_data.get("club")
    score = 0.5 if club else 0
    detail = [
        f"  Клуб: {club.get('name', '—') if club else 'не состоит'} → {score} баллов",
        f"  ИТОГО модуль 7: {score:.2f}/0.5",
    ]
    return {"score": score, "detail": detail}


# ═══════════════════════════════════════════════════════════════════════════════
# ИТОГОВЫЙ РАСЧЁТ
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_psi(player_data: dict, api: Any) -> dict:
    brawlers = player_data.get("brawlers", [])
    total_trophies = player_data.get("trophies", 0)
    tag = player_data.get("tag", "")

    m1 = calc_module_1(brawlers, total_trophies)
    m2 = calc_module_2(player_data)
    m3 = calc_module_3(player_data, brawlers, api, tag)
    m4 = calc_module_4(brawlers)
    m5 = calc_module_5(player_data, brawlers)
    m6 = calc_module_6(brawlers)
    m7 = calc_module_7(player_data)

    raw = m1["score"] + m2["score"] + m3["score"] + m4["score"] + m5["score"] + m6["score"] + m7["score"]

    if raw <= 100:
        psi = raw
    else:
        psi = 100 + (raw - 100) * 0.1

    return {
        "psi": round(psi, 2),
        "raw": round(raw, 2),
        "modules": {
            "1_praims": {"score": m1["score"], "detail": m1["detail"]},
            "2_ranked": {"score": m2["score"], "detail": m2["detail"]},
            "3_top_world": {"score": m3["score"], "detail": m3["detail"]},
            "4_veteran": {"score": m4["score"], "detail": m4["detail"]},
            "5_quantitative": {"score": m5["score"], "detail": m5["detail"]},
            "6_qualitative": {"score": m6["score"], "detail": m6["detail"]},
            "7_club": {"score": m7["score"], "detail": m7["detail"]},
        },
    }
