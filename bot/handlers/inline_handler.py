from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

router = Router()
from bot.utils.api import get_player, get_psi


@router.inline_query()
async def inline_query(query: InlineQuery):
    tag = query.query.strip()
    if not tag:
        return

    if not tag.startswith("#"):
        tag = "#" + tag

    try:
        player = get_player(tag)
        psi = get_psi(tag)

        text = (
            f"👤 <b>{player['name']}</b>\n"
            f"🏆 {player['trophies']} трофеев\n"
            f"🧮 PSI: <b>{psi['psi']}</b>\n"
            f"🎯 {player.get('highestAllTimeRankedRankName', '—')}"
        )

        result = InlineQueryResultArticle(
            id=tag,
            title=f"{player['name']} — PSI {psi['psi']}",
            description=f"{player['trophies']} трофеев | {player.get('highestAllTimeRankedRankName', '—')}",
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML"
            )
        )
        await query.answer([result], cache_time=60)
    except Exception:
        pass