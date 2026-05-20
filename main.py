"""
Brawl Stars Stats v2.0 — Главный файл.
1. Полная информация об игроке
2. Расчёт PSI (Player Skill Index) с детализацией модулей
3. Конвертер тегов (игрок + команда)
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))
from lib.bs_api import BrawlStarsAPI, BrawlStarsAPIError, NotFoundError
from lib.bs_tag_converter import LongToCodeConverter
from lib.psi_calculator import calculate_psi
from tools.player_info import show_player_full

API_KEY = os.getenv("BS_API_KEY")

if not API_KEY:
    print("Ошибка: BS_API_KEY не найден в .env")
    exit(1)


def print_sep(title: str = "") -> None:
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'-'*60}")


def menu_player_info(api: BrawlStarsAPI) -> None:
    """Пункт 1: Полная информация об игроке."""
    print()
    tag = input("  Введи тег игрока: ").strip()
    if not tag:
        return
    if not tag.startswith("#"):
        tag = "#" + tag
    show_player_full(api, tag)


def menu_psi(api: BrawlStarsAPI) -> None:
    """Пункт 2: Расчёт PSI с детализацией модулей."""
    print()
    tag = input("  Введи тег игрока: ").strip()
    if not tag:
        return
    if not tag.startswith("#"):
        tag = "#" + tag

    try:
        player = api.get_player(tag)
    except NotFoundError:
        print(f"\n  Игрок {tag} не найден.")
        return
    except BrawlStarsAPIError as e:
        print(f"\n  Ошибка API: {e}")
        return

    print_sep(f"РАСЧЁТ PSI: {player.get('name', '?')} ({player.get('tag', '?')})")

    try:
        result = calculate_psi(player, api)
    except Exception as e:
        print(f"\n  Ошибка при расчёте PSI: {e}")
        return

    psi = result["psi"]
    raw = result["raw"]
    mod = result["modules"]

    if psi >= 100:
        level = "👑 GODLIKE"
    elif psi >= 80:
        level = "🔥 PRO"
    elif psi >= 60:
        level = "💎 SEMI-PRO"
    elif psi >= 40:
        level = "🎯 EXPERIENCED"
    elif psi >= 20:
        level = "📈 INTERMEDIATE"
    else:
        level = "🌱 BEGINNER"

    print(f"\n  ИТОГ: {psi:.2f} PSI — {level}")
    print(f"  Сырые баллы: {raw:.2f}/120.5")
    print()

    # Вывод каждого модуля с детализацией
    module_names = [
        ("1. ПРАЙМЫ", "1_praims", 30),
        ("2. RANKED", "2_ranked", 37),
        ("3. ТОП-МИР + РЕГИОН", "3_top_world", 20),
        ("4. ВЕТЕРАН", "4_veteran", 8),
        ("5. КОЛИЧЕСТВЕННЫЕ", "5_quantitative", 15),
        ("6. КАЧЕСТВЕННЫЕ", "6_qualitative", 10),
        ("7. КЛУБ", "7_club", 0.5),
    ]

    for name, key, max_val in module_names:
        m = mod[key]
        print(f"  ▸ {name}: {m['score']:.2f}/{max_val}")
        for line in m["detail"]:
            print(line)
        print()


def menu_tag_converter() -> None:
    """Пункт 3: Конвертер тегов."""
    player_conv = LongToCodeConverter.player_converter()
    team_conv = LongToCodeConverter.team_converter()

    while True:
        print()
        print("  ┌──────────────────────────────────┐")
        print("  │  КОНВЕРТЕР ТЕГОВ                 │")
        print("  ├──────────────────────────────────┤")
        print("  │  1. Тег игрока → ID              │")
        print("  │  2. ID → Тег игрока              │")
        print("  │  3. Тег команды → ID             │")
        print("  │  4. ID → Тег команды             │")
        print("  │  0. Назад                        │")
        print("  └──────────────────────────────────┘")

        choice = input("  Выбери: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            tag = input("  Тег игрока: ").strip()
            if not tag.startswith("#"):
                tag = "#" + tag
            hi, lo = player_conv.to_id_pair(tag)
            if hi == -1 and lo == -1:
                print(f"  Ошибка: невалидный тег")
            else:
                print(f"  high={hi}, low={lo}")

        elif choice == "2":
            try:
                hi = int(input("  high (0-255): "))
                lo = int(input("  low: "))
            except ValueError:
                print("  Ошибка: введи целые числа")
                continue
            tag = player_conv.to_code(hi, lo)
            if tag is None:
                print("  Ошибка: high должен быть 0-255")
            else:
                print(f"  Тег: {tag}")

        elif choice == "3":
            tag = input("  Тег команды: ").strip()
            if not tag.startswith("X"):
                tag = "X" + tag
            hi, lo = team_conv.to_id_pair(tag)
            if hi == -1 and lo == -1:
                print(f"  Ошибка: невалидный тег")
            else:
                print(f"  high={hi}, low={lo}")

        elif choice == "4":
            try:
                hi = int(input("  high: "))
                lo = int(input("  low: "))
            except ValueError:
                print("  Ошибка: введи целые числа")
                continue
            tag = team_conv.to_code(hi, lo)
            if tag is None:
                print("  Ошибка: невалидный ID")
            else:
                print(f"  Тег: {tag}")

        else:
            print("  Неверный выбор.")


def main():
    api = BrawlStarsAPI(API_KEY)

    try:
        while True:
            print()
            print("=" * 60)
            print("  BRAWL STARS STATS v2.0")
            print("=" * 60)
            print("  1. Полная информация об игроке")
            print("  2. Расчёт PSI (Player Skill Index)")
            print("  3. Конвертер тегов (игрок + команда)")
            print("  0. Выход")
            print("-" * 60)

            choice = input("  Выбери действие: ").strip()

            if choice == "0":
                print("  Выход.")
                break
            elif choice == "1":
                menu_player_info(api)
            elif choice == "2":
                menu_psi(api)
            elif choice == "3":
                menu_tag_converter()
            else:
                print("  Неверный выбор. Введи 0-3.")

    except KeyboardInterrupt:
        print("\n  Выход.")
    finally:
        api.close()


if __name__ == "__main__":
    main()