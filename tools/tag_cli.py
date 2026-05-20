"""
Интерактивный CLI конвертер тегов Brawl Stars.
Использует lib/bs_tag_converter.py для конвертации.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.bs_tag_converter import LongToCodeConverter


def main():
    converter = LongToCodeConverter.player_converter()
    team_converter = LongToCodeConverter.team_converter()

    while True:
        print()
        print("=" * 50)
        print("КОНВЕРТЕР ТЕГОВ BRAWL STARS")
        print("=" * 50)
        print("1. Тег игрока → ID")
        print("2. ID → Тег игрока")
        print("3. Тег команды → ID")
        print("4. ID → Тег команды")
        print("0. Выход")
        print("-" * 50)

        choice = input("Выбери действие (0-4): ").strip()

        if choice == "0":
            print("Выход.")
            break

        elif choice == "1":
            tag = input("Введи тег игрока (например #2P0LYQ8J): ").strip()
            if not tag:
                print("Ошибка: пустой ввод")
                continue
            if not tag.startswith("#"):
                tag = "#" + tag

            hi, lo = converter.to_id_pair(tag)
            if hi == -1 and lo == -1:
                print(f"Ошибка: невалидный тег '{tag}'")
            else:
                print(f"Тег: {tag}")
                print(f"ID:  high={hi}, low={lo}")

        elif choice == "2":
            try:
                hi = int(input("Введи high (0-255): ").strip())
                lo = int(input("Введи low (например 530379): ").strip())
            except ValueError:
                print("Ошибка: введи целые числа")
                continue

            tag = converter.to_code(hi, lo)
            if tag is None:
                print(f"Ошибка: невалидный ID (high должен быть 0-255)")
            else:
                print(f"ID:   high={hi}, low={lo}")
                print(f"Тег: {tag}")

        elif choice == "3":
            tag = input("Введи тег команды (например XRHEZ4): ").strip()
            if not tag:
                print("Ошибка: пустой ввод")
                continue
            if not tag.startswith("X"):
                tag = "X" + tag

            hi, lo = team_converter.to_id_pair(tag)
            if hi == -1 and lo == -1:
                print(f"Ошибка: невалидный тег '{tag}'")
            else:
                print(f"Тег: {tag}")
                print(f"ID:  high={hi}, low={lo}")

        elif choice == "4":
            try:
                hi = int(input("Введи high: ").strip())
                lo = int(input("Введи low: ").strip())
            except ValueError:
                print("Ошибка: введи целые числа")
                continue

            tag = team_converter.to_code(hi, lo)
            if tag is None:
                print(f"Ошибка: невалидный ID")
            else:
                print(f"ID:   high={hi}, low={lo}")
                print(f"Тег: {tag}")

        else:
            print("Неверный выбор. Введи 0-4.")


if __name__ == "__main__":
    main()