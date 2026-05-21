"""
Brawl Stars Stats — Flask v2.2
"""
import json
import os
import random
import sys
import time
from lang import LANG

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_caching import Cache

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.bs_api import BrawlStarsAPI, BrawlStarsAPIError, NotFoundError
from lib.psi_calculator import calculate_psi
from lib.bs_tag_converter import LongToCodeConverter
from lib.db import add_search, update_user_psi, get_top_users, save_player_psi, get_top_player_psi

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24).hex()

REDIS_URL = os.getenv("REDIS_URL", "")
if REDIS_URL:
    app.config["CACHE_TYPE"] = "RedisCache"
    app.config["CACHE_REDIS_URL"] = REDIS_URL
else:
    app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
cache = Cache(app)

RECENT_KEY = "recent_players"


def get_lang():
    lang = request.args.get("lang", session.get("lang", "ru"))
    session["lang"] = lang
    return LANG.get(lang, LANG["ru"])


def get_api():
    return BrawlStarsAPI(os.getenv("BS_API_KEY", ""))


def add_recent(player_data):
    recent = session.get(RECENT_KEY, [])
    entry = {"tag": player_data.get("tag"), "name": player_data.get("name"), "trophies": player_data.get("trophies"),
             "timestamp": int(time.time())}
    recent = [e for e in recent if e["tag"] != entry["tag"]]
    recent.insert(0, entry)
    session[RECENT_KEY] = recent[:10]


def get_average_stats():
    return {
        "avg_trophies": 15000, "avg_exp": 120, "avg_3v3": 2000,
        "avg_solo": 500, "avg_duo": 700, "avg_brawlers": 85,
        "avg_p1": 30, "avg_p2": 8, "avg_p3": 1,
        "avg_ranked": "DIAMOND", "avg_elo": 3500,
    }


@app.route("/")
def index():
    lang = get_lang()
    recent = session.get(RECENT_KEY, [])
    top_psi = get_top_player_psi(10)
    return render_template("index.html", recent=recent, lang=lang, top_psi=top_psi)


@app.route("/set-lang/<l>")
def set_lang(l):
    session["lang"] = l
    return redirect(request.referrer or "/")


@app.route("/player", methods=["POST"])
def player():
    tag = request.form.get("tag", "").strip()
    if not tag.startswith("#"): tag = "#" + tag
    return redirect(url_for("player_get", tag=tag))


@app.route("/player/<tag>")
@cache.memoize(timeout=120)
def player_get(tag):
    if not tag.startswith("#"): tag = "#" + tag
    lang = get_lang()

    api = get_api()
    try:
        player_data = api.get_player(tag)
        psi_result = calculate_psi(player_data, api)
        add_recent(player_data)

        # Сохраняем в БД
        add_search(0, tag, player_data["name"], psi_result["psi"], player_data["trophies"])
        save_player_psi(tag, player_data["name"], psi_result["psi"], player_data["trophies"])

        club_info = None
        if player_data.get("club"):
            try:
                club_info = api.get_club(player_data["club"]["tag"])
            except:
                pass
        battlelog = None
        try:
            battlelog = api.get_battlelog(tag)
        except:
            pass
        avg = get_average_stats()
    except NotFoundError:
        return render_template("index.html", error=lang["player_not_found"] + f": {tag}", lang=lang)
    except BrawlStarsAPIError as e:
        return render_template("index.html", error=str(e), lang=lang)
    finally:
        api.close()

    tips = []
    mod = psi_result["modules"]
    if mod["1_praims"]["score"] < 15: tips.append(
        ("Праймы", "Подними бравлеров до P2 (2000 трофеев). Каждый P2 на D/F даёт +4.5 балла."))
    if mod["2_ranked"]["score"] < 14: tips.append(("Ranked", "Подними ранг до Legendary I — это даст 14 баллов."))
    if mod["3_top_world"]["score"] < 10: tips.append(
        ("Топы", "Попади в топ-200 России хотя бы на 3 бравлерах (+6 баллов)."))
    if mod["5_quantitative"]["score"] < 10: tips.append(
        ("Колич.", "Увеличь уровень аккаунта до 300+ и трофеи до 70k+."))

    return render_template("player.html", player=player_data, psi=psi_result, club=club_info, battlelog=battlelog,
                           tag=tag, lang=lang, avg=avg, tips=tips)


@app.route("/api/player/<tag>")
def api_player(tag):
    if not tag.startswith("#"): tag = "#" + tag
    api = get_api()
    try:
        player_data = api.get_player(tag)
        psi_result = calculate_psi(player_data, api)
        return jsonify({"success": True, "player": player_data, "psi": psi_result})
    except NotFoundError:
        return jsonify({"success": False, "error": "Not found"})
    except BrawlStarsAPIError as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        api.close()


@app.route("/compare", methods=["GET", "POST"])
def compare():
    lang = get_lang()
    result = error = None
    if request.method == "POST":
        tag1 = request.form.get("tag1", "").strip()
        tag2 = request.form.get("tag2", "").strip()
        if not tag1.startswith("#"): tag1 = "#" + tag1
        if not tag2.startswith("#"): tag2 = "#" + tag2
        api = get_api()
        try:
            p1 = api.get_player(tag1);
            p2 = api.get_player(tag2)
            psi1 = calculate_psi(p1, api);
            psi2 = calculate_psi(p2, api)
            result = {"p1": p1, "p2": p2, "psi1": psi1, "psi2": psi2}
        except Exception as e:
            error = str(e)
        finally:
            api.close()
    return render_template("compare.html", result=result, error=error, lang=lang)


@app.route("/tag-converter", methods=["GET", "POST"])
def tag_converter():
    lang = get_lang()
    result = error = None
    if request.method == "POST":
        action = request.form.get("action")
        pc = LongToCodeConverter.player_converter()
        tc = LongToCodeConverter.team_converter()
        try:
            if action == "player_to_id":
                tag = request.form.get("tag", "").strip()
                if not tag.startswith("#"): tag = "#" + tag
                hi, lo = pc.to_id_pair(tag);
                result = f"high={hi}, low={lo}"
            elif action == "id_to_player":
                hi, lo = int(request.form.get("hi", 0)), int(request.form.get("lo", 0))
                result = f"Тег: {pc.to_code(hi, lo)}"
            elif action == "team_to_id":
                tag = request.form.get("tag", "").strip()
                if not tag.startswith("X"): tag = "X" + tag
                hi, lo = tc.to_id_pair(tag);
                result = f"high={hi}, low={lo}"
            elif action == "id_to_team":
                hi, lo = int(request.form.get("hi", 0)), int(request.form.get("lo", 0))
                result = f"Тег: {tc.to_code(hi, lo)}"
        except Exception as e:
            error = str(e)
    return render_template("tag_converter.html", result=result, error=error, lang=lang)


@app.route("/rankings")
@cache.cached(timeout=300)
def rankings():
    lang = get_lang()
    api = get_api()
    try:
        ru = api.get_player_rankings("ru", limit=50)
        gl = api.get_player_rankings("global", limit=50)
    except:
        ru = gl = {"items": []}
    finally:
        api.close()
    return render_template("rankings.html", ru=ru.get("items", []), global_=gl.get("items", []), lang=lang)


@app.route("/brawlers")
@cache.cached(timeout=600)
def brawlers_page():
    lang = get_lang()
    path = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}
    return render_template("brawlers.html", brawlers=data, lang=lang)


@app.route("/club/<tag>")
def club_page(tag):
    lang = get_lang()
    if not tag.startswith("#"): tag = "#" + tag
    api = get_api()
    try:
        club = api.get_club(tag)
        members = api.get_club_members(tag)
        members_list = members.get("items", [])
    except Exception as e:
        return render_template("index.html", error=str(e), lang=lang)
    finally:
        api.close()
    return render_template("club.html", club=club, members=members_list, lang=lang)


@app.route("/random")
def random_player():
    api = get_api()
    try:
        rankings = api.get_player_rankings("ru", limit=200)
        items = rankings.get("items", [])
        if items:
            player = random.choice(items)
            return redirect(url_for("player_get", tag=player.get("tag", "")))
    except:
        pass
    finally:
        api.close()
    return redirect("/")


@app.route("/mini-game")
def mini_game():
    lang = get_lang()
    api = get_api()

    if session.get("mini_p1"):
        p1_tag = session.get("mini_p1")
        p2_tag = session.get("mini_p2")
        correct = session.get("mini_correct")
        psi1_val = session.get("mini_psi1")
        psi2_val = session.get("mini_psi2")

        try:
            player1 = api.get_player(p1_tag)
            player2 = api.get_player(p2_tag)
        except:
            player1 = player2 = None

        for k in ["mini_p1", "mini_p2", "mini_correct", "mini_psi1", "mini_psi2"]:
            session.pop(k, None)

        return render_template("mini_game.html",
                               p1=player1, p2=player2,
                               correct=correct,
                               psi1_val=psi1_val, psi2_val=psi2_val,
                               show_result=True, lang=lang)

    try:
        rankings = api.get_player_rankings("ru", limit=100)
        items = rankings.get("items", [])
        p1_data = random.choice(items)
        p2_data = random.choice(items)
        while p2_data["tag"] == p1_data["tag"]:
            p2_data = random.choice(items)

        player1 = api.get_player(p1_data["tag"])
        player2 = api.get_player(p2_data["tag"])
        psi1 = calculate_psi(player1, api)
        psi2 = calculate_psi(player2, api)
        correct = 1 if psi1["psi"] > psi2["psi"] else 2 if psi2["psi"] > psi1["psi"] else 0

        session["mini_p1"] = player1["tag"]
        session["mini_p2"] = player2["tag"]
        session["mini_correct"] = correct
        session["mini_psi1"] = psi1["psi"]
        session["mini_psi2"] = psi2["psi"]

        return render_template("mini_game.html",
                               p1=player1, p2=player2,
                               correct=correct,
                               psi1_val=psi1["psi"], psi2_val=psi2["psi"],
                               show_result=False, lang=lang)
    except Exception as e:
        return render_template("index.html", error=str(e), lang=lang)
    finally:
        api.close()


@app.route("/calculator")
def calculator_page():
    lang = get_lang()
    return render_template("calculator.html", lang=lang)


@app.route("/profile")
def profile_page():
    lang = get_lang()
    uid = request.args.get("uid", "")
    data = None
    if uid:
        from lib.db import get_or_create_user, get_favorites, get_friends, get_search_history, get_friends_activity, \
            get_badges, get_cards
        user = get_or_create_user(int(uid), "")
        if user:
            data = {
                "user": user,
                "favorites": get_favorites(user["id"]),
                "friends": get_friends(user["id"]),
                "history": get_search_history(user["id"], 20),
                "activity": get_friends_activity(user["id"], 10),
                "badges": get_badges(user["id"]),
                "cards": get_cards(user["id"]),
            }
    return render_template("profile.html", lang=lang, data=data)


@app.route("/api/tiers")
def api_tiers():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify({})


@app.route("/badge/<tag>")
def psi_badge(tag):
    if not tag.startswith("#"): tag = "#" + tag
    api = get_api()
    try:
        player = api.get_player(tag)
        psi = calculate_psi(player, api)

        psi_val = psi["psi"]
        if psi_val >= 100:
            color, bg, level = "#ffc107", "#1a1a00", "👑 GODLIKE"
        elif psi_val >= 80:
            color, bg, level = "#ff4444", "#1a0000", "🔥 PRO"
        elif psi_val >= 60:
            color, bg, level = "#aa00ff", "#0a001a", "💎 SEMI-PRO"
        elif psi_val >= 40:
            color, bg, level = "#00c853", "#001a00", "🎯 EXPERIENCED"
        elif psi_val >= 20:
            color, bg, level = "#ff8800", "#1a0a00", "📈 INTERMEDIATE"
        else:
            color, bg, level = "#8b949e", "#0d1117", "🌱 BEGINNER"

        name = player['name'][:18]
        tag_clean = player['tag']
        trophies = player['trophies']
        brawlers_count = len(player.get('brawlers', []))

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
            <defs>
                <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="{bg}"/>
                    <stop offset="100%" stop-color="#0d1117"/>
                </linearGradient>
                <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="rgba(255,255,255,0)" />
                    <stop offset="50%" stop-color="rgba(255,255,255,0.1)" />
                    <stop offset="100%" stop-color="rgba(255,255,255,0)" />
                </linearGradient>
            </defs>
            <rect width="400" height="200" rx="15" fill="url(#bg)" stroke="{color}" stroke-width="3"/>
            <rect width="400" height="200" rx="15" fill="url(#shine)"/>
            <text x="200" y="35" text-anchor="middle" fill="{color}" font-size="16" font-weight="bold" font-family="Arial">{name}</text>
            <text x="200" y="55" text-anchor="middle" fill="#8b949e" font-size="11" font-family="Arial">{tag_clean}</text>
            <text x="200" y="100" text-anchor="middle" fill="{color}" font-size="48" font-weight="bold" font-family="Arial">PSI {psi_val}</text>
            <text x="200" y="125" text-anchor="middle" fill="#8b949e" font-size="14" font-family="Arial">{level}</text>
            <rect x="30" y="145" width="340" height="3" rx="2" fill="#21262d"/>
            <rect x="30" y="145" width="{psi_val / 120.5 * 340}" height="3" rx="2" fill="{color}"/>
            <text x="50" y="175" fill="#8b949e" font-size="12" font-family="Arial">🏆 {trophies}</text>
            <text x="200" y="175" text-anchor="middle" fill="#8b949e" font-size="12" font-family="Arial">🤖 {brawlers_count} бравлеров</text>
            <text x="350" y="175" text-anchor="end" fill="#8b949e" font-size="12" font-family="Arial">BrawlStats v2.2</text>
        </svg>'''

        return svg, 200, {"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=3600"}
    except Exception as e:
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200">
            <rect width="400" height="200" rx="15" fill="#0d1117" stroke="#ff4444" stroke-width="2"/>
            <text x="200" y="100" text-anchor="middle" fill="#ff4444" font-size="16" font-family="Arial">Игрок не найден</text>
        </svg>'''
        return svg, 404, {"Content-Type": "image/svg+xml"}


@app.route("/top-brawlers")
def top_brawlers_page():
    lang = get_lang()
    # Из player_psi берём топ-10 игроков
    top_players = get_top_player_psi(10)
    brawler_counts = {}

    api = get_api()
    for p in top_players:
        try:
            player = api.get_player(p["tag"])
            for b in player.get("brawlers", [])[:3]:
                name = b["name"]
                if name not in brawler_counts:
                    brawler_counts[name] = 0
                brawler_counts[name] += 1
        except:
            pass
    api.close()

    sorted_brawlers = sorted(brawler_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    return render_template("top_brawlers.html", brawlers=sorted_brawlers, lang=lang)


@app.route("/badge-constructor")
def badge_constructor():
    lang = get_lang()
    return render_template("badge_constructor.html", lang=lang)


@app.route("/api/badge-custom/<tag>")
def psi_badge_custom(tag):
    if not tag.startswith("#"): tag = "#" + tag
    color = request.args.get("color", "ffc107")
    bg = request.args.get("bg", "0d1117")
    size = request.args.get("size", "medium")
    style = request.args.get("style", "modern")
    text = request.args.get("text", "PSI")
    show_name = request.args.get("name", "1")
    show_trophies = request.args.get("trophies", "1")
    show_rank = request.args.get("rank", "1")
    show_club = request.args.get("club", "0")
    show_praims = request.args.get("praims", "0")
    show_brawlers = request.args.get("brawlers", "0")
    show_progress = request.args.get("progress", "1")

    sizes = {"small": (200, 120), "medium": (400, 220), "large": (600, 320)}
    w, h = sizes.get(size, (400, 220))

    api = get_api()
    try:
        player = api.get_player(tag)
        psi = calculate_psi(player, api)
        psi_val = psi["psi"]
        name = player['name'][:22]
        trophies = player['trophies']
        rank_name = player.get('highestAllTimeRankedRankName', '—')
        club_name = player.get('club', {}).get('name', '—')
        brawlers_list = player.get('brawlers', [])
        brawlers_count = len(brawlers_list)
        p1 = sum(1 for b in brawlers_list if b.get('trophies', 0) >= 1000)
        p2 = sum(1 for b in brawlers_list if b.get('trophies', 0) >= 2000)
        p3 = sum(1 for b in brawlers_list if b.get('trophies', 0) >= 3000)
    except:
        psi_val = "?"
        name = "Не найден"
        trophies = 0
        rank_name = "—"
        club_name = "—"
        brawlers_count = 0
        p1 = p2 = p3 = 0

    # Строим SVG
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
    svg += f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#{bg}"/><stop offset="100%" stop-color="#1a1a2e"/></linearGradient></defs>'
    svg += f'<rect width="{w}" height="{h}" rx="15" fill="url(#bg)" stroke="#{color}" stroke-width="3"/>'

    y = 30
    if show_name == "1":
        svg += f'<text x="{w / 2}" y="{y}" text-anchor="middle" fill="#{color}" font-size="16" font-weight="bold" font-family="Arial">{name}</text>'
        y += 25

    svg += f'<text x="{w / 2}" y="{y + 20}" text-anchor="middle" fill="#{color}" font-size="36" font-weight="bold" font-family="Arial">{text} {psi_val}</text>'
    y += 40

    info_y = y + 15
    info_items = []
    if show_trophies == "1":
        info_items.append(f'🏆 {trophies}')
    if show_rank == "1":
        info_items.append(f'🎯 {rank_name}')
    if show_club == "1":
        info_items.append(f'👥 {club_name[:15]}')
    if show_praims == "1":
        info_items.append(f'P1:{p1} P2:{p2} P3:{p3}')
    if show_brawlers == "1":
        info_items.append(f'🤖 {brawlers_count}')

    if info_items:
        info_text = ' · '.join(info_items)
        svg += f'<text x="{w / 2}" y="{info_y}" text-anchor="middle" fill="#8b949e" font-size="11" font-family="Arial">{info_text}</text>'
        y = info_y + 20
    else:
        y = info_y

    if show_progress == "1" and psi_val != "?":
        bar_y = y + 10
        svg += f'<rect x="{w * 0.1}" y="{bar_y}" width="{w * 0.8}" height="4" rx="2" fill="#21262d"/>'
        progress = min(psi_val / 120.5, 1)
        svg += f'<rect x="{w * 0.1}" y="{bar_y}" width="{w * 0.8 * progress}" height="4" rx="2" fill="#{color}"/>'
        y = bar_y + 15

    svg += f'<text x="{w * 0.1}" y="{h - 15}" fill="#8b949e" font-size="10" font-family="Arial">BrawlStats v2.2</text>'
    svg += '</svg>'

    return svg, 200, {"Content-Type": "image/svg+xml", "Cache-Control": "public, max-age=3600"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
