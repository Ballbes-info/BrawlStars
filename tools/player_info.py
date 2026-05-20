"""
Полная информация об игроке Brawl Stars.
Выводит ВСЕ данные которые возвращает API.
Использует lib/bs_api.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.bs_api import BrawlStarsAPI, BrawlStarsAPIError, NotFoundError

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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


def print_all(data, indent: int = 0) -> None:
    """Рекурсивно выводит все поля."""
    tab = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                print(f"{tab}{k}:")
                print_all(v, indent + 1)
            else:
                print(f"{tab}{k}: {v}")
    elif isinstance(data, list):
        if not data:
            print(f"{tab}[]")
        else:
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    name = item.get("name", item.get("tag", f"[{i}]"))
                    print(f"{tab}[{i}] {name}")
                    print_all(item, indent + 1)
                else:
                    print(f"{tab}[{i}]: {item}")
    else:
        print(f"{tab}{data}")


def show_player_full(api: BrawlStarsAPI, tag: str) -> None:
    """Показать все данные игрока."""

    # 1. Профиль
    try:
        player = api.get_player(tag)
    except NotFoundError:
        print(f"\nИгрок {tag} не найден.")
        return
    except BrawlStarsAPIError as e:
        print(f"\nОшибка: {e}")
        return

    print_sep("1. ПОЛНЫЙ ПРОФИЛЬ (get_player)")
    for key, value in player.items():
        if key == "brawlers":
            continue
        if key == "club":
            if value:
                print(f"\n  ▸ КЛУБ:")
                print_all(value, indent=2)
            else:
                print("  club: null")
        elif isinstance(value, (dict, list)):
            print(f"  {key}:")
            print_all(value, indent=2)
        else:
            print(f"  {key}: {value}")

    # 2. Бравлеры
    brawlers = player.get("brawlers", [])
    print_sep(f"2. БРАВЛЕРЫ ({len(brawlers)}) — ПОЛНОСТЬЮ")
    for b in brawlers:
        name = b.get("name", "?")
        print(f"\n  ▸ {name}:")
        print_all(b, indent=2)

    # 3. Баттлог
    print_sep("3. ИСТОРИЯ БОЁВ (get_battlelog)")
    try:
        battlelog = api.get_battlelog(tag)
        items = battlelog.get("items", [])
        print(f"  Всего записей: {len(items)}")
        for battle in items:
            event = battle.get("event", {})
            battle_data = battle.get("battle", {})
            mode = event.get("mode", "?")
            map_name = event.get("map", "?")
            result = battle_data.get("result", "?")
            trophy_change = battle_data.get("trophyChange", 0)
            sign = "+" if trophy_change and trophy_change > 0 else ""
            print(f"  {mode} | {map_name} | {result} | {sign}{trophy_change}")
    except NotFoundError:
        print("  История боёв скрыта игроком")
    except BrawlStarsAPIError as e:
        print(f"  Ошибка: {e}")

    # 4. Клуб
    club = player.get("club")
    if club:
        print_sep("4. КЛУБ — ПОЛНАЯ ИНФОРМАЦИЯ (get_club)")
        try:
            club_full = api.get_club(club["tag"])
            print_all(club_full, indent=1)
        except BrawlStarsAPIError as e:
            print(f"  Ошибка: {e}")

        print_sep("5. УЧАСТНИКИ КЛУБА (get_club_members)")
        try:
            members = api.get_club_members(club["tag"])
            items = members.get("items", [])
            print(f"  Всего участников: {len(items)}")
            for m in items:
                print(f"  {m.get('name', '?'):<15} {m.get('role', '?'):<12} {m.get('trophies', 0)} трофеев  тег: {m.get('tag', '?')}")
        except BrawlStarsAPIError as e:
            print(f"  Ошибка: {e}")
    else:
        print_sep("4. КЛУБ")
        print("  Не состоит в клубе")

    # 5. ПОЗИЦИЯ В РЕЙТИНГАХ
    print_sep("6. ПОЗИЦИЯ В РЕЙТИНГАХ")

    # 5a. Общий рейтинг России
    try:
        rankings = api.get_player_rankings("ru", limit=200)
        items_list = rankings.get("items", [])
        found = False
        for p in items_list:
            if p.get("tag") == tag:
                print(f"  Общий рейтинг России: {p['rank']} место — {p['trophies']} \U0001f3c6")
                found = True
                break
        if not found:
            print(f"  Общий рейтинг России: не входит в топ-200")
    except BrawlStarsAPIError as e:
        print(f"  Общий рейтинг: ошибка — {e}")

    # 5b. Рейтинг по бравлерам
    print()
    print(f"  Рейтинги по бравлерам (топ-200 мира / топ-200 России):")
    print(f"  {'Бравлер':<20} {'Трофеи':>6} {'Мир':>10} {'Россия':>10}")
    print(f"  {'-'*50}")

    def norm(t: str) -> str:
        return t.replace("#", "").replace("O", "0").replace("o", "0").upper()

    original_tag = player.get("tag", tag)
    normalized_original = norm(original_tag)

    sorted_brawlers = sorted(brawlers, key=lambda b: b.get("trophies", 0), reverse=True)

    for b in sorted_brawlers:
        brawler_id = b.get("id")
        brawler_name = b.get("name", "?")
        brawler_trophies = b.get("trophies", 0)

        if brawler_trophies == 0:
            break

        rank_world = None
        rank_ru = None

        try:
            world_rankings = api.get_brawler_rankings("global", brawler_id, limit=200)
            for p in world_rankings.get("items", []):
                if norm(p.get("tag", "")) == normalized_original:
                    rank_world = p.get("rank")
                    break
        except BrawlStarsAPIError:
            pass

        try:
            ru_rankings = api.get_brawler_rankings("ru", brawler_id, limit=200)
            for p in ru_rankings.get("items", []):
                if norm(p.get("tag", "")) == normalized_original:
                    rank_ru = p.get("rank")
                    break
        except BrawlStarsAPIError:
            pass

        world_str = f"#{rank_world}" if rank_world else "—"
        ru_str = f"#{rank_ru}" if rank_ru else "—"

        if rank_world or rank_ru:
            print(f"  {brawler_name:<20} {brawler_trophies:>6} {world_str:>10} {ru_str:>10}")
        else:
            break

    # 6. СВОДНАЯ СТАТИСТИКА
    print_sep("7. СВОДНАЯ СТАТИСТИКА ПО БРАВЛЕРАМ")

    total_brawlers = len(brawlers)
    max_gadgets = total_brawlers * 2
    max_starpowers = total_brawlers * 2
    max_hypercharges = total_brawlers * 1

    total_gadgets = 0
    total_starpowers = 0
    total_hypercharges = 0
    total_gears = 0
    max_gears_level_sum = 0
    brawlers_with_skin = 0
    max_power_count = 0
    total_prestige = 0

    count_3000plus = 0
    count_2000plus = 0
    count_1000plus = 0

    for b in brawlers:
        gadgets = b.get("gadgets", [])
        starpowers = b.get("starPowers", [])
        hypercharges = b.get("hyperCharges", [])
        gears = b.get("gears", [])
        trophies_b = b.get("trophies", 0)

        total_gadgets += len(gadgets)
        total_starpowers += len(starpowers)
        total_hypercharges += len(hypercharges)
        total_gears += len(gears)
        max_gears_level_sum += sum(g.get("level", 0) for g in gears)

        if b.get("skin") and b["skin"].get("name") not in (b.get("name"), None):
            brawlers_with_skin += 1

        if b.get("power") == 11:
            max_power_count += 1

        total_prestige += b.get("prestigeLevel", 0)

        if trophies_b >= 3000:
            count_3000plus += 1
        if trophies_b >= 2000:
            count_2000plus += 1
        if trophies_b >= 1000:
            count_1000plus += 1

    total_collectibles = total_gadgets + total_starpowers + total_hypercharges
    max_collectibles = max_gadgets + max_starpowers + max_hypercharges

    print(f"  ┌─────────────────────────────────────────┐")
    print(f"  │ Бравлеров:           {total_brawlers:>4}                    │")
    print(f"  │ Макс. сила (11):     {max_power_count:>4} из {total_brawlers:<4}             │")
    print(f"  │ Сумм. престиж:       {total_prestige:>4}                    │")
    print(f"  ├─────────────────────────────────────────┤")
    print(f"  │ Гаджетов:            {total_gadgets:>4} из {max_gadgets:<4}  ({total_gadgets*100//max_gadgets:>3}%)         │")
    print(f"  │ Звёздных сил:        {total_starpowers:>4} из {max_starpowers:<4}  ({total_starpowers*100//max_starpowers:>3}%)         │")
    print(f"  │ Гиперзарядов:        {total_hypercharges:>4} из {max_hypercharges:<4}  ({total_hypercharges*100//max_hypercharges:>3}%)         │")
    print(f"  │ Всего пассивок:      {total_collectibles:>4} из {max_collectibles:<4}  ({total_collectibles*100//max_collectibles:>3}%)         │")
    print(f"  ├─────────────────────────────────────────┤")
    print(f"  │ Gears установлено:   {total_gears:>4}                    │")
    print(f"  │ Сумма уровней:       {max_gears_level_sum:>4}                    │")
    print(f"  │ Надето скинов:       {brawlers_with_skin:>4}                    │")
    print(f"  ├─────────────────────────────────────────┤")
    print(f"  │ Бравлеров 3000+:     {count_3000plus:>4}                    │")
    print(f"  │ Бравлеров 2000+:     {count_2000plus:>4}                    │")
    print(f"  │ Бравлеров 1000+:     {count_1000plus:>4}                    │")
    print(f"  └─────────────────────────────────────────┘")
    print(f"  ⚠️ Коллекция скинов/пинов/спреев недоступна через API")

    # 7. КУБКИ ЗА ПОСЛЕДНИЕ БОИ
    print_sep("8. КУБКИ ЗА ПОСЛЕДНИЕ БОИ (~неделя)")
    try:
        battlelog = api.get_battlelog(tag)
        items_log = battlelog.get("items", [])
        total_trophy_change = 0
        wins = 0
        losses = 0
        for battle in items_log:
            battle_data = battle.get("battle", {})
            change = battle_data.get("trophyChange", 0)
            result = battle_data.get("result", "?")
            if result == "victory":
                wins += 1
            elif result == "defeat":
                losses += 1
            total_trophy_change += change if change else 0

        print(f"  Боёв в истории:        {len(items_log)}")
        print(f"  Побед:                  {wins}")
        print(f"  Поражений:              {losses}")
        print(f"  Изменение трофеев:      {total_trophy_change:+}")
    except BrawlStarsAPIError:
        print("  Не удалось загрузить")

    print_sep("ГОТОВО")


if __name__ == "__main__":
    api = BrawlStarsAPI(API_KEY)
    try:
        while True:
            print()
            tag = input("Введи тег (#XXXXXX) или 0 для выхода: ").strip()
            if tag == "0":
                break
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = "#" + tag
            show_player_full(api, tag)
    except KeyboardInterrupt:
        print("\nВыход.")
    finally:
        api.close()