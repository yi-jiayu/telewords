import logging
from asyncio import gather
from os import getenv

import httpx
import sanic.response
from sanic import Sanic

from game import Game, get_leaderboard_scores, format_scores

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
    if "start" in text and (chat_id > 0 or bot_name.lower() in text.lower()):
        await start_game(chat_id, text)
    elif "stop" in text and (chat_id > 0 or bot_name.lower() in text.lower()):
        await stop_game(chat_id)
    else:
        game = Game.find(chat_id)
        if game:
            name = update["message"]["from"]["first_name"]
            user_id = update["message"]["from"]["id"]
            await make_guess(game, chat_id, user_id, name, text)


async def make_guess(game, chat_id, user_id, name, text: str):
    messages = game.guess(user_id, name, text)
    finished = False
    if game.is_finished():
        finished = True
        messages.extend(game.stop())
        game.delete()
    else:
        game.save()
    await transduce(chat_id, messages)
    if finished:
        await send_all_time_scores(chat_id)


async def start_game(chat_id, text):
    kwargs = {}
    args = text.split()
    if len(args) > 1:
        try:
            num_rounds = int(args[1])
            kwargs["num_rounds"] = num_rounds
        except ValueError:
            pass
    game = Game(chat_id, **kwargs)
    games[chat_id] = game
    messages = game.start()
    game.save()
    await transduce(chat_id, messages)


async def stop_game(chat_id):
    game = Game.find(chat_id)
    if game is None:
        await send_message(
            chat_id,
            f"No game in progress! To start a new game, tag {bot_name} and say start!",
        )
        return
    messages = game.stop()
    game.delete()
    await transduce(chat_id, messages)
    await send_all_time_scores(chat_id)


async def send_all_time_scores(chat_id):
    scores = get_leaderboard_scores(chat_id)
    await send_message(chat_id, f"*All-time scores*\n{format_scores(scores)}")


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
    r = await httpx.post(url, data=params)
    if not 200 <= r.status_code < 400:
        logging.error(r.text)


async def transduce(chat_id, messages):
    replies = (send_message(chat_id, text, parse_mode) for text, parse_mode in messages)
    await gather(*replies)


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
