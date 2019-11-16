import logging
from os import getenv

import httpx
import sanic.response
from sanic import Sanic

from game import Game
from dictionary import get_definition

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
    if text.startswith("/startgame"):
        await start_game(chat_id)
    elif text.startswith("/stop"):
        await stop_game(chat_id)
    elif chat_id in games:
        name = update["message"]["from"]["first_name"]
        user_id = update["message"]["from"]["id"]
        await guess(chat_id, user_id, name, text)


async def guess(chat_id, user_id, name, text: str):
    game = games[chat_id]
    text = text.lower()
    result = game.make_guess(user_id, name, text)
    if result is not None:
        points = result
        message = f"{text.capitalize()}: {points} points!"
        definition = get_definition(text)
        if definition is not None:
            message += "\n" + definition
        await make_telegram_request(
            "sendMessage", {"chat_id": chat_id, "text": message},
        )
        await show_scores(chat_id)
        await send_grid(chat_id, game)
        if game.is_finished():
            await stop_game(chat_id)


async def show_scores(chat_id):
    if chat_id in games:
        game = games[chat_id]
        await make_telegram_request(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": game.format_scores(),
                "parse_mode": "Markdown",
            },
        )


async def start_game(chat_id):
    game = Game()
    games[chat_id] = game
    await send_grid(chat_id, game)


async def send_grid(chat_id, game):
    if game.remaining_rounds == 1:
        message = "Last round!"
    elif game.remaining_rounds == 0:
        message = "Game over!"
    else:
        message = f"{game.remaining_rounds} rounds remaining!"
    await make_telegram_request(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": game.format_grid() + "\n" + message,
            "parse_mode": "Markdown",
        },
    )


async def stop_game(chat_id):
    if chat_id in games:
        game = games[chat_id]
        await make_telegram_request(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": f"*Final scores*\n\n" + game.format_scores(),
                "parse_mode": "Markdown",
            },
        )
        del games[chat_id]


async def make_telegram_request(method, params):
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=params)
    if not 200 <= r.status_code < 400:
        logging.error(r.text)


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
