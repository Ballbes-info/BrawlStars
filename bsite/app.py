"""
Brawl Stars Stats — Flask v2.2
"""
import os, sys, time, json, random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_caching import Cache
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.bs_api import BrawlStarsAPI, BrawlStarsAPIError, NotFoundError
from lib.psi_calculator import calculate_psi
from lib.bs_tag_converter import LongToCodeConverter

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

LANG = {
    "ru": {
        "search": "Поиск", "compare": "Сравнение", "rankings": "Рейтинги",
        "brawlers": "Бравлеры", "converter": "Конвертер", "random": "Случайный",
        "input_tag": "Введи тег игрока", "find": "Найти",
        "player_not_found": "Игрок не найден",
        "psi": "Player Skill Index", "trophies": "Трофеи",
    },
    "en": {
        "search": "Search", "compare": "Compare", "rankings": "Rankings",
        "brawlers": "Brawlers", "converter": "Converter", "random": "Random",
        "input_tag": "Enter player tag", "find": "Find",
        "player_not_found": "Player not found",
        "psi": "Player Skill Index", "trophies": "Trophies",
    }
}

def get_lang():
    lang = request.args.get("lang", session.get("lang", "ru"))
    session["lang"] = lang
    return LANG.get(lang, LANG["ru"])

def get_api():
    return BrawlStarsAPI(os.getenv("BS_API_KEY", ""))

def add_recent(player_data):
    recent = session.get(RECENT_KEY, [])
    entry = {"tag": player_data.get("tag"), "name": player_data.get("name"), "trophies": player_data.get("trophies"), "timestamp": int(time.time())}
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
    return render_template("index.html", recent=recent, lang=lang)

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
        club_info = None
        if player_data.get("club"):
            try: club_info = api.get_club(player_data["club"]["tag"])
            except: pass
        battlelog = None
        try: battlelog = api.get_battlelog(tag)
        except: pass
        avg = get_average_stats()
    except NotFoundError:
        return render_template("index.html", error=lang["player_not_found"] + f": {tag}", lang=lang)
    except BrawlStarsAPIError as e:
        return render_template("index.html", error=str(e), lang=lang)
    finally:
        api.close()

    tips = []
    mod = psi_result["modules"]
    if mod["1_praims"]["score"] < 15: tips.append(("Праймы", "Подними бравлеров до P2 (2000 трофеев). Каждый P2 на D/F даёт +4.5 балла."))
    if mod["2_ranked"]["score"] < 14: tips.append(("Ranked", "Подними ранг до Legendary I — это даст 14 баллов."))
    if mod["3_top_world"]["score"] < 10: tips.append(("Топы", "Попади в топ-200 России хотя бы на 3 бравлерах (+6 баллов)."))
    if mod["5_quantitative"]["score"] < 10: tips.append(("Колич.", "Увеличь уровень аккаунта до 300+ и трофеи до 70k+."))

    return render_template("player.html", player=player_data, psi=psi_result, club=club_info, battlelog=battlelog, tag=tag, lang=lang, avg=avg, tips=tips)

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
            p1 = api.get_player(tag1); p2 = api.get_player(tag2)
            psi1 = calculate_psi(p1, api); psi2 = calculate_psi(p2, api)
            result = {"p1": p1, "p2": p2, "psi1": psi1, "psi2": psi2}
        except Exception as e: error = str(e)
        finally: api.close()
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
                tag = request.form.get("tag","").strip()
                if not tag.startswith("#"): tag = "#" + tag
                hi, lo = pc.to_id_pair(tag); result = f"high={hi}, low={lo}"
            elif action == "id_to_player":
                hi, lo = int(request.form.get("hi",0)), int(request.form.get("lo",0))
                result = f"Тег: {pc.to_code(hi, lo)}"
            elif action == "team_to_id":
                tag = request.form.get("tag","").strip()
                if not tag.startswith("X"): tag = "X" + tag
                hi, lo = tc.to_id_pair(tag); result = f"high={hi}, low={lo}"
            elif action == "id_to_team":
                hi, lo = int(request.form.get("hi",0)), int(request.form.get("lo",0))
                result = f"Тег: {tc.to_code(hi, lo)}"
        except Exception as e: error = str(e)
    return render_template("tag_converter.html", result=result, error=error, lang=lang)

@app.route("/rankings")
@cache.cached(timeout=300)
def rankings():
    lang = get_lang()
    api = get_api()
    try:
        ru = api.get_player_rankings("ru", limit=50)
        gl = api.get_player_rankings("global", limit=50)
    except: ru = gl = {"items": []}
    finally: api.close()
    return render_template("rankings.html", ru=ru.get("items",[]), global_=gl.get("items",[]), lang=lang)

@app.route("/brawlers")
@cache.cached(timeout=600)
def brawlers_page():
    lang = get_lang()
    path = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")
    try:
        with open(path, "r", encoding="utf-8") as f: data = json.load(f)
    except: data = {}
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
    finally: api.close()
    return render_template("club.html", club=club, members=members_list, lang=lang)

@app.route("/random")
def random_player():
    api = get_api()
    try:
        rankings = api.get_player_rankings("ru", limit=200)
        items = rankings.get("items", [])
        if items:
            player = random.choice(items)
            return redirect(url_for("player_get", tag=player.get("tag","")))
    except: pass
    finally: api.close()
    return redirect("/")

@app.route("/mini-game")
def mini_game():
    lang = get_lang()
    api = get_api()

    # Если есть сохранённая игра — показываем результат
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

        # Очищаем сессию
        for k in ["mini_p1", "mini_p2", "mini_correct", "mini_psi1", "mini_psi2"]:
            session.pop(k, None)

        return render_template("mini_game.html",
                             p1=player1, p2=player2,
                             correct=correct,
                             psi1_val=psi1_val, psi2_val=psi2_val,
                             show_result=True, lang=lang)

    # Новая игра
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

        # Сохраняем в сессию
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)