import logging
from asyncio import gather
from os import getenv

import httpx
import sanic.response
from sanic import Sanic

from dictionary import get_definition
from game import Game
from letters import common_words

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
    elif chat_id in games:
        name = update["message"]["from"]["first_name"]
        user_id = update["message"]["from"]["id"]
        await guess(chat_id, user_id, name, text)


async def guess(chat_id, user_id, name, text: str):
    game = games[chat_id]
    text = text.lower()
    result = game.make_guess(user_id, name, text)
    if result is not None:
        word, points = result
        message = f"{word.capitalize()}: {points} points!"
        if word not in common_words:
            definition = get_definition(text)
            if definition is not None:
                message += "\n" + definition
        await gather(
            send_message(chat_id, message),
            show_scores(chat_id),
            send_grid(chat_id, game),
        )
        if game.is_finished():
            await stop_game(chat_id)


async def show_scores(chat_id):
    if chat_id in games:
        game = games[chat_id]
        await send_message(chat_id, game.format_scores())


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
    if game.remaining_rounds > 0:
        message += "\n\n" + f"<em>Hint: {game.get_hint()}</em>"
    await send_message(
        chat_id, f"<pre>{game.format_grid()}</pre>" + "\n" + message, parse_mode="HTML"
    )


async def stop_game(chat_id):
    if chat_id in games:
        game = games[chat_id]
        del games[chat_id]
        if game.scores:
            await send_message(chat_id, f"*Final scores*\n\n" + game.format_scores())
        await report_remaining_words(chat_id, game)


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


async def report_remaining_words(chat_id, game):
    remaining_words = game.longest_remaining_words()
    if not remaining_words:
        return
    text = "Here are some words you missed:"
    for word in remaining_words:
        definition = get_definition(word)
        if definition:
            word += "\n" + definition
        text += "\n\n" + word
    await send_message(chat_id, text)


async def make_telegram_request(method, params):
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=params)
    if not 200 <= r.status_code < 400:
        logging.error(r.text)


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
