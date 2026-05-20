"""
Brawl Stars Stats — Flask v2.1
"""
import os, sys, time, json, random
from flask import Flask, render_template, request, jsonify, session
from flask_caching import Cache
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.bs_api import BrawlStarsAPI, BrawlStarsAPIError, NotFoundError
from lib.psi_calculator import calculate_psi
from lib.bs_tag_converter import LongToCodeConverter

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24).hex()
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
cache = Cache(app)

RECENT_KEY = "recent_players"


def get_api():
    return BrawlStarsAPI(os.getenv("BS_API_KEY", ""))


def add_recent(player_data):
    recent = session.get(RECENT_KEY, [])
    entry = {
        "tag": player_data.get("tag"),
        "name": player_data.get("name"),
        "trophies": player_data.get("trophies"),
        "timestamp": int(time.time()),
    }
    recent = [e for e in recent if e["tag"] != entry["tag"]]
    recent.insert(0, entry)
    session[RECENT_KEY] = recent[:10]


@app.route("/")
def index():
    recent = session.get(RECENT_KEY, [])
    return render_template("index.html", recent=recent)


@app.route("/player", methods=["POST"])
def player():
    tag = request.form.get("tag", "").strip()
    if not tag.startswith("#"):
        tag = "#" + tag

    api = get_api()
    try:
        player_data = api.get_player(tag)
        psi_result = calculate_psi(player_data, api)
        add_recent(player_data)

        club_info = None
        if player_data.get("club"):
            try:
                club_info = api.get_club(player_data["club"]["tag"])
            except Exception:
                pass

        battlelog = None
        try:
            battlelog = api.get_battlelog(tag)
        except Exception:
            pass

    except NotFoundError:
        return render_template("index.html", error=f"Игрок {tag} не найден")
    except BrawlStarsAPIError as e:
        return render_template("index.html", error=str(e))
    finally:
        api.close()

    return render_template(
        "player.html",
        player=player_data,
        psi=psi_result,
        club=club_info,
        battlelog=battlelog,
        tag=tag,
    )


@app.route("/player/<tag>")
def player_get(tag):
    if not tag.startswith("#"):
        tag = "#" + tag

    api = get_api()
    try:
        player_data = api.get_player(tag)
        psi_result = calculate_psi(player_data, api)
        add_recent(player_data)
        club_info = None
        if player_data.get("club"):
            try:
                club_info = api.get_club(player_data["club"]["tag"])
            except Exception:
                pass
        battlelog = None
        try:
            battlelog = api.get_battlelog(tag)
        except Exception:
            pass
    except Exception as e:
        return render_template("index.html", error=str(e))
    finally:
        api.close()

    return render_template(
        "player.html",
        player=player_data,
        psi=psi_result,
        club=club_info,
        battlelog=battlelog,
        tag=tag,
    )


@app.route("/api/player/<tag>")
def api_player(tag):
    if not tag.startswith("#"):
        tag = "#" + tag

    api = get_api()
    try:
        player_data = api.get_player(tag)
        psi_result = calculate_psi(player_data, api)
        return jsonify({"success": True, "player": player_data, "psi": psi_result})
    except NotFoundError:
        return jsonify({"success": False, "error": "Игрок не найден"})
    except BrawlStarsAPIError as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        api.close()


@app.route("/compare", methods=["GET", "POST"])
def compare():
    result = None
    error = None

    if request.method == "POST":
        tag1 = request.form.get("tag1", "").strip()
        tag2 = request.form.get("tag2", "").strip()
        if not tag1.startswith("#"): tag1 = "#" + tag1
        if not tag2.startswith("#"): tag2 = "#" + tag2

        api = get_api()
        try:
            p1 = api.get_player(tag1)
            p2 = api.get_player(tag2)
            psi1 = calculate_psi(p1, api)
            psi2 = calculate_psi(p2, api)
            result = {"p1": p1, "p2": p2, "psi1": psi1, "psi2": psi2}
        except Exception as e:
            error = str(e)
        finally:
            api.close()

    return render_template("compare.html", result=result, error=error)


@app.route("/tag-converter", methods=["GET", "POST"])
def tag_converter():
    result = None
    error = None

    if request.method == "POST":
        action = request.form.get("action")
        player_conv = LongToCodeConverter.player_converter()
        team_conv = LongToCodeConverter.team_converter()

        try:
            if action == "player_to_id":
                tag = request.form.get("tag", "").strip()
                if not tag.startswith("#"): tag = "#" + tag
                hi, lo = player_conv.to_id_pair(tag)
                result = f"high={hi}, low={lo}"
            elif action == "id_to_player":
                hi = int(request.form.get("hi", 0))
                lo = int(request.form.get("lo", 0))
                tag = player_conv.to_code(hi, lo)
                result = f"Тег: {tag}"
            elif action == "team_to_id":
                tag = request.form.get("tag", "").strip()
                if not tag.startswith("X"): tag = "X" + tag
                hi, lo = team_conv.to_id_pair(tag)
                result = f"high={hi}, low={lo}"
            elif action == "id_to_team":
                hi = int(request.form.get("hi", 0))
                lo = int(request.form.get("lo", 0))
                tag = team_conv.to_code(hi, lo)
                result = f"Тег: {tag}"
        except Exception as e:
            error = str(e)

    return render_template("tag_converter.html", result=result, error=error)


@app.route("/rankings")
@cache.cached(timeout=300)
def rankings():
    api = get_api()
    try:
        ru_rankings = api.get_player_rankings("ru", limit=50)
        global_rankings = api.get_player_rankings("global", limit=50)
    except Exception:
        ru_rankings = {"items": []}
        global_rankings = {"items": []}
    finally:
        api.close()

    return render_template(
        "rankings.html",
        ru=ru_rankings.get("items", []),
        global_=global_rankings.get("items", []),
    )


@app.route("/brawlers")
@cache.cached(timeout=600)
def brawlers_page():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "tiers.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    return render_template("brawlers.html", brawlers=data)


@app.route("/random")
def random_player():
    api = get_api()
    try:
        rankings = api.get_player_rankings("ru", limit=200)
        items = rankings.get("items", [])
        if items:
            player = random.choice(items)
            return player_get(player.get("tag", ""))
    except Exception:
        pass
    finally:
        api.close()

    return render_template("index.html", error="Не удалось найти случайного игрока")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)