import logging
from asyncio import gather
from os import getenv

import httpx
import sanic.response
from sanic import Sanic

from game import Game

app = Sanic()
bot_token = getenv("TELEGRAM_BOT_TOKEN")
bot_name = getenv("TELEGRAM_BOT_USERNAME")
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
    if "start" in text and bot_name in text:
        await start_game(chat_id, text)
    elif "stop" in text and bot_name in text:
        await stop_game(chat_id)
    elif text.startswith("/hint"):
        await send_hint(chat_id)
    elif chat_id in games:
        name = update["message"]["from"]["first_name"]
        user_id = update["message"]["from"]["id"]
        await make_guess(chat_id, user_id, name, text)


async def make_guess(chat_id, user_id, name, text: str):
    game = games[chat_id]
    await transduce(chat_id, game.guess(user_id, name, text))
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
            chat_id,
            f'No game in progress! You can start a new game by saying "start" and tagging {bot_name}.',
        )


async def start_game(chat_id, text):
    kwargs = {}
    args = text.split()
    if len(args) > 1:
        try:
            num_rounds = int(args[1])
            kwargs["num_rounds"] = num_rounds
        except ValueError:
            pass
    game = Game(**kwargs)
    games[chat_id] = game
    await transduce(chat_id, game.start())


async def stop_game(chat_id):
    if chat_id in games:
        game = games[chat_id]
        del games[chat_id]
        await transduce(chat_id, game.stop())


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


async def transduce(chat_id, messages):
    replies = (send_message(chat_id, text, parse_mode) for text, parse_mode in messages)
    await gather(*replies)


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
