"""
Brawl Stars API Wrapper
Обёртка для официального Brawl Stars API.
Использует urllib (без requests).
"""
import time
import json
from typing import Optional, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class BrawlStarsAPIError(Exception):
    pass

class RateLimitError(BrawlStarsAPIError):
    pass

class NotFoundError(BrawlStarsAPIError):
    pass

class ForbiddenError(BrawlStarsAPIError):
    pass


class BrawlStarsAPI:
    BASE_URL = "https://api.brawlstars.com/v1"

    def __init__(self, api_key: str, timeout: int = 10, max_retries: int = 3) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

    @staticmethod
    def _encode_tag(tag: str) -> str:
        if "%23" in tag:
            return tag
        return tag.replace("#", "%23")

    def _request(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        retries = 0

        while retries <= self.max_retries:
            try:
                req = Request(url)
                req.add_header("Authorization", f"Bearer {self.api_key}")
                req.add_header("Accept", "application/json")

                with urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        return json.loads(resp.read())

                    if resp.status == 403:
                        raise ForbiddenError("Невалидный API ключ")
                    if resp.status == 404:
                        raise NotFoundError(f"Ресурс не найден: {endpoint}")
                    if resp.status == 429:
                        retries += 1
                        if retries > self.max_retries:
                            raise RateLimitError("Превышен лимит запросов")
                        time.sleep(2 ** (retries - 1))
                        continue

                    raise BrawlStarsAPIError(f"Ошибка API: {resp.status}")

            except HTTPError as e:
                if e.code == 403:
                    raise ForbiddenError("Невалидный API ключ")
                if e.code == 404:
                    raise NotFoundError(f"Ресурс не найден: {endpoint}")
                if e.code == 429:
                    retries += 1
                    if retries > self.max_retries:
                        raise RateLimitError("Превышен лимит запросов")
                    time.sleep(2 ** (retries - 1))
                    continue
                raise BrawlStarsAPIError(f"Ошибка API: {e.code}")

            except URLError as e:
                retries += 1
                if retries > self.max_retries:
                    raise BrawlStarsAPIError(f"Ошибка соединения: {e}")
                time.sleep(1)

        raise BrawlStarsAPIError("Неизвестная ошибка")

    def get_player(self, tag: str) -> Dict[str, Any]:
        return self._request(f"/players/{self._encode_tag(tag)}")

    def get_battlelog(self, tag: str) -> Dict[str, Any]:
        return self._request(f"/players/{self._encode_tag(tag)}/battlelog")

    def get_club(self, tag: str) -> Dict[str, Any]:
        return self._request(f"/clubs/{self._encode_tag(tag)}")

    def get_club_members(self, tag: str) -> Dict[str, Any]:
        return self._request(f"/clubs/{self._encode_tag(tag)}/members")

    def get_brawlers(self) -> Dict[str, Any]:
        return self._request("/brawlers")

    def get_brawler(self, brawler_id: int) -> Dict[str, Any]:
        return self._request(f"/brawlers/{brawler_id}")

    def get_player_rankings(self, country: str = "global", limit: Optional[int] = None) -> Dict[str, Any]:
        endpoint = f"/rankings/{country}/players"
        if limit:
            endpoint += f"?limit={limit}"
        return self._request(endpoint)

    def get_club_rankings(self, country: str = "global", limit: Optional[int] = None) -> Dict[str, Any]:
        endpoint = f"/rankings/{country}/clubs"
        if limit:
            endpoint += f"?limit={limit}"
        return self._request(endpoint)

    def get_brawler_rankings(self, country: str = "global", brawler_id: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        if brawler_id is None:
            raise ValueError("brawler_id обязателен")
        endpoint = f"/rankings/{country}/brawlers/{brawler_id}"
        if limit:
            endpoint += f"?limit={limit}"
        return self._request(endpoint)

    def get_event_rotation(self) -> Dict[str, Any]:
        return self._request("/events/rotation")

    def close(self) -> None:
        pass

    def __enter__(self) -> "BrawlStarsAPI":
        return self

    def __exit__(self, *args) -> None:
        self.close()