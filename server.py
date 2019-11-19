import logging
from asyncio import gather
from os import getenv

import httpx
import sanic.response
from sanic import Sanic

from game import Game

app = Sanic()
bot_token = getenv("TELEGRAM_BOT_TOKEN")
games = {}


@app.route("/", methods=["POST"])
async def handle(request):
    update = request.json
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        await handle_text(update, text)
    return sanic.response.json({})


async def handle_text(update, text):
    chat_id = update["message"]["chat"]["id"]
    if text.startswith("/start"):
        await start_game(chat_id)
    elif text.startswith("/stop"):
        await stop_game(chat_id)
    elif text.startswith("/hint"):
        await send_hint(chat_id)
    elif chat_id in games:
        name = update["message"]["from"]["first_name"]
        user_id = update["message"]["from"]["id"]
        await make_guess(chat_id, user_id, name, text)


async def make_guess(chat_id, user_id, name, text: str):
    game = games[chat_id]
    replies = (
        send_message(chat_id, text, parse_mode)
        for text, parse_mode in game.guess(user_id, name, text)
    )
    await gather(*replies)
    if game.is_finished():
        await stop_game(chat_id)


async def send_hint(chat_id):
    if chat_id in games:
        game = games[chat_id]
        await send_message(
            chat_id, f"<em>Hint: {game.get_hint()}</em>", parse_mode="HTML"
        )
    else:
        await send_message(
            chat_id, "No game in progress! You can start a new game with /start."
        )


async def start_game(chat_id):
    game = Game()
    games[chat_id] = game
    replies = (
        send_message(chat_id, text, parse_mode) for text, parse_mode in game.start()
    )
    await gather(*replies)


async def stop_game(chat_id):
    if chat_id in games:
        game = games[chat_id]
        del games[chat_id]
        replies = (
            send_message(chat_id, text, parse_mode) for text, parse_mode in game.stop()
        )
        await gather(*replies)


async def send_message(chat_id, text, parse_mode="Markdown"):
    params = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        params["parse_mode"] = parse_mode
    await make_telegram_request(
        "sendMessage", params,
    )


async def make_telegram_request(method, params):
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=params)
    if not 200 <= r.status_code < 400:
        logging.error(r.text)


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
