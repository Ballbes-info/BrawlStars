"""
Brawl Stars Stats — Telegram-бот v2.0
"""
import os, sys, asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

session = AiohttpSession(proxy="socks5://127.0.0.1:10808")
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    from bot.handlers import (
        start, select_handler, player, psi, club, compare, help_handler,
        brawlers, rankings, random_player, events, stats,
        inline_handler,
        card, chart, weakest, progress, top_brawlers, duel, fun,
        favorite, friends, top, subscribe, calculator, daily,
        collect, badges, quiz, tournament
    )
    dp.include_router(start.router)
    dp.include_router(select_handler.router)
    dp.include_router(player.router)
    dp.include_router(psi.router)
    dp.include_router(club.router)
    dp.include_router(compare.router)
    dp.include_router(help_handler.router)
    dp.include_router(brawlers.router)
    dp.include_router(rankings.router)
    dp.include_router(random_player.router)
    dp.include_router(events.router)
    dp.include_router(stats.router)
    dp.include_router(inline_handler.router)
    dp.include_router(card.router)
    dp.include_router(chart.router)
    dp.include_router(weakest.router)
    dp.include_router(progress.router)
    dp.include_router(top_brawlers.router)
    dp.include_router(duel.router)
    dp.include_router(fun.router)
    dp.include_router(favorite.router)
    dp.include_router(friends.router)
    dp.include_router(top.router)
    dp.include_router(subscribe.router)
    dp.include_router(calculator.router)
    dp.include_router(daily.router)
    dp.include_router(collect.router)
    dp.include_router(badges.router)
    dp.include_router(quiz.router)
    dp.include_router(tournament.router)

    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())