"""
Обновление IP в .env перед запуском бота.
"""
import os
from urllib.request import urlopen


def get_current_ip():
    return urlopen("https://api.ipify.org").read().decode().strip()


def update_env(ip: str):
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    with open(env_path, "r") as f:
        lines = f.readlines()

    with open(env_path, "w") as f:
        for line in lines:
            if line.startswith("CURRENT_IP="):
                f.write(f"CURRENT_IP={ip}\n")
            else:
                f.write(line)

    print(f"IP обновлён: {ip}")


if __name__ == "__main__":
    ip = get_current_ip()
    update_env(ip)