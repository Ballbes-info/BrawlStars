"""
Brawl Stars API Wrapper
Обёртка для официального Brawl Stars API.
Поддерживает все эндпоинты: игроки, клубы, бравлеры, рейтинги, события.
"""
import time
from typing import Optional, Dict, List, Any
import requests


class BrawlStarsAPIError(Exception):
    """Базовое исключение для ошибок API."""
    pass


class RateLimitError(BrawlStarsAPIError):
    """Превышен лимит запросов (429)."""
    pass


class NotFoundError(BrawlStarsAPIError):
    """Ресурс не найден (404)."""
    pass


class ForbiddenError(BrawlStarsAPIError):
    """Невалидный API ключ (403)."""
    pass


class BrawlStarsAPI:
    """
    Клиент для Brawl Stars API.

    Args:
        api_key: API ключ с developer.brawlstars.com
        timeout: таймаут запроса в секундах
        max_retries: количество повторных попыток при 429
    """

    BASE_URL = "https://api.brawlstars.com/v1"

    def __init__(
        self,
        api_key: str,
        timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            }
        )

    # ──────────────────────────────────────────────────────────
    # СЛУЖЕБНЫЕ МЕТОДЫ
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _encode_tag(tag: str) -> str:
        """
        Кодирует тег для URL: # → %23.
        Если тег уже содержит %23, возвращает как есть.
        """
        if "%23" in tag:
            return tag
        return tag.replace("#", "%23")

    def _request(self, endpoint: str) -> Dict[str, Any]:
        """
        Выполняет GET-запрос к API с обработкой ошибок и повторными попытками.

        Args:
            endpoint: путь эндпоинта, например "/players/%232P0LYQ8J"

        Returns:
            Распарсенный JSON-ответ

        Raises:
            ForbiddenError: невалидный API ключ (403)
            NotFoundError: ресурс не найден (404)
            RateLimitError: превышен лимит запросов (429)
            BrawlStarsAPIError: прочие ошибки API
        """
        url = f"{self.BASE_URL}{endpoint}"
        retries = 0

        while retries <= self.max_retries:
            try:
                response = self.session.get(url, timeout=self.timeout)

                if response.status_code == 200:
                    return response.json()

                if response.status_code == 403:
                    raise ForbiddenError(
                        "Невалидный API ключ. Получи ключ на developer.brawlstars.com"
                    )

                if response.status_code == 404:
                    raise NotFoundError(
                        f"Ресурс не найден: {endpoint}"
                    )

                if response.status_code == 429:
                    retries += 1
                    if retries > self.max_retries:
                        raise RateLimitError(
                            f"Превышен лимит запросов после {self.max_retries} попыток"
                        )
                    # Экспоненциальная задержка: 1s, 2s, 4s...
                    wait_time = 2 ** (retries - 1)
                    time.sleep(wait_time)
                    continue

                # Прочие ошибки
                raise BrawlStarsAPIError(
                    f"Ошибка API: {response.status_code} — {response.text[:200]}"
                )

            except requests.exceptions.Timeout:
                retries += 1
                if retries > self.max_retries:
                    raise BrawlStarsAPIError(
                        f"Таймаут запроса после {self.max_retries} попыток"
                    )
                time.sleep(1)
                continue

            except requests.exceptions.RequestException as e:
                raise BrawlStarsAPIError(f"Ошибка соединения: {e}")

        # Недостижимо, но для линтера
        raise BrawlStarsAPIError("Неизвестная ошибка")

    # ──────────────────────────────────────────────────────────
    # ИГРОКИ
    # ──────────────────────────────────────────────────────────

    def get_player(self, tag: str) -> Dict[str, Any]:
        """
        Получить полный профиль игрока.

        Args:
            tag: тег игрока (#XXXXXXXX)

        Returns:
            Словарь с данными профиля: имя, трофеи, уровень, бравлеры, клуб...
        """
        encoded_tag = self._encode_tag(tag)
        return self._request(f"/players/{encoded_tag}")

    def get_battlelog(self, tag: str) -> Dict[str, Any]:
        """
        Получить историю последних боёв игрока.

        Args:
            tag: тег игрока (#XXXXXXXX)

        Returns:
            Словарь со списком последних боёв (items)
        """
        encoded_tag = self._encode_tag(tag)
        return self._request(f"/players/{encoded_tag}/battlelog")

    # ──────────────────────────────────────────────────────────
    # КЛУБЫ
    # ──────────────────────────────────────────────────────────

    def get_club(self, tag: str) -> Dict[str, Any]:
        """
        Получить информацию о клубе.

        Args:
            tag: тег клуба (#XXXXXXXX)

        Returns:
            Словарь с данными клуба: название, описание, трофеи, количество участников...
        """
        encoded_tag = self._encode_tag(tag)
        return self._request(f"/clubs/{encoded_tag}")

    def get_club_members(self, tag: str) -> Dict[str, Any]:
        """
        Получить список участников клуба.

        Args:
            tag: тег клуба (#XXXXXXXX)

        Returns:
            Словарь со списком участников (items), каждый с ролью, трофеями, тегом...
        """
        encoded_tag = self._encode_tag(tag)
        return self._request(f"/clubs/{encoded_tag}/members")

    # ──────────────────────────────────────────────────────────
    # БРАВЛЕРЫ
    # ──────────────────────────────────────────────────────────

    def get_brawlers(self) -> Dict[str, Any]:
        """
        Получить список всех бравлеров.

        Returns:
            Словарь со списком бравлеров (items): id, name, power, rank...
        """
        return self._request("/brawlers")

    def get_brawler(self, brawler_id: int) -> Dict[str, Any]:
        """
        Получить информацию о конкретном бравлере.

        Args:
            brawler_id: ID бравлера (например 16000000 для Shelly)

        Returns:
            Словарь с данными бравлера
        """
        return self._request(f"/brawlers/{brawler_id}")

    # ──────────────────────────────────────────────────────────
    # РЕЙТИНГИ
    # ──────────────────────────────────────────────────────────

    def get_player_rankings(
        self,
        country: str = "global",
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Получить рейтинг игроков по стране или глобальный.

        Args:
            country: код страны (ru, us, de...) или "global"
            limit: количество записей (по умолчанию — сколько отдаст API)

        Returns:
            Словарь со списком игроков в рейтинге (items)
        """
        endpoint = f"/rankings/{country}/players"
        if limit is not None:
            endpoint += f"?limit={limit}"
        return self._request(endpoint)

    def get_club_rankings(
        self,
        country: str = "global",
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Получить рейтинг клубов по стране или глобальный.

        Args:
            country: код страны или "global"
            limit: количество записей

        Returns:
            Словарь со списком клубов в рейтинге (items)
        """
        endpoint = f"/rankings/{country}/clubs"
        if limit is not None:
            endpoint += f"?limit={limit}"
        return self._request(endpoint)

    def get_brawler_rankings(
        self,
        country: str = "global",
        brawler_id: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Получить рейтинг по конкретному бравлеру.

        Args:
            country: код страны или "global"
            brawler_id: ID бравлера (16000000 для Shelly)
            limit: количество записей

        Returns:
            Словарь со списком игроков в рейтинге по бравлеру (items)
        """
        if brawler_id is None:
            raise ValueError("brawler_id обязателен для рейтинга бравлеров")
        endpoint = f"/rankings/{country}/brawlers/{brawler_id}"
        if limit is not None:
            endpoint += f"?limit={limit}"
        return self._request(endpoint)

    # ──────────────────────────────────────────────────────────
    # СОБЫТИЯ
    # ──────────────────────────────────────────────────────────

    def get_event_rotation(self) -> Dict[str, Any]:
        """
        Получить текущую и предстоящую ротацию событий/карт.

        Returns:
            Словарь со списком событий (текущие + предстоящие)
        """
        return self._request("/events/rotation")

    # ──────────────────────────────────────────────────────────
    # ЗАКРЫТИЕ
    # ──────────────────────────────────────────────────────────

    def close(self) -> None:
        """Закрыть HTTP-сессию."""
        self.session.close()

    def __enter__(self) -> "BrawlStarsAPI":
        return self

    def __exit__(self, *args) -> None:
        self.close()