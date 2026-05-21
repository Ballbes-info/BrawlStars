import os, sys, json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import importlib.util

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BS_API_KEY", "")
BASE_URL = "https://api.brawlstars.com/v1"


def _request(endpoint):
    req = Request(f"{BASE_URL}{endpoint}")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Accept", "application/json")
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        raise Exception(f"API error: {e.code}")


def get_player(tag: str):
    return _request(f"/players/{tag.replace('#', '%23')}")


def get_psi(tag: str):
    psi_path = os.path.join(os.path.dirname(__file__), "..", "..", "lib", "psi_calculator.py")
    spec = importlib.util.spec_from_file_location("psi_calculator", psi_path)
    psi_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(psi_mod)

    player = get_player(tag)
    api = type('obj', (object,), {
        'get_player': lambda self, t: player,
        'get_brawler_rankings': lambda self, c, id, limit: _request(f"/rankings/{c}/brawlers/{id}?limit={limit}"),
        'get_player_rankings': lambda self, c, limit: _request(f"/rankings/{c}/players?limit={limit}")
    })()
    return psi_mod.calculate_psi(player, api)


def get_club_members(tag: str):
    return _request(f"/clubs/{tag.replace('#', '%23')}/members").get("items", [])


def get_rankings(country: str, limit: int = 10):
    return _request(f"/rankings/{country}/players?limit={limit}").get("items", [])


def get_events():
    return _request("/events/rotation")