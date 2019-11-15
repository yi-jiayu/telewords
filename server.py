import logging
from os import getenv

import requests
import sanic.response
from sanic import Sanic

from game import Game

app = Sanic()
bot_token = getenv("TELEGRAM_BOT_TOKEN")
games = {}


@app.route("/", methods=["POST"])
async def test(request):
    update = request.json
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        handle_text(update, text)
    return sanic.response.json({})


def handle_text(update, text):
    chat_id = update["message"]["chat"]["id"]
    if text.startswith("/startgame"):
        start_game(chat_id)
    elif text.startswith('/stop'):
        stop_game(chat_id)
    elif chat_id in games:
        name = update["message"]["from"]["first_name"]
        user_id = update["message"]["from"]["id"]
        guess(chat_id, user_id, name, text)


def guess(chat_id, user_id, name, text: str):
    game = games[chat_id]
    text = text.lower()
    result = game.make_guess(user_id, name, text)
    if result is not None:
        points = result
        make_telegram_request(
            "sendMessage",
            {"chat_id": chat_id, "text": f"{text.capitalize()}: {points} points!"},
        )
        show_scores(chat_id)
        make_telegram_request(
            "sendMessage",
            {"chat_id": chat_id, "text": game.format_grid(), "parse_mode": "Markdown"},
        )


def show_scores(chat_id):
    if chat_id in games:
        game = games[chat_id]
        make_telegram_request(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": game.format_scores(),
                "parse_mode": "Markdown",
            },
        )


def start_game(chat_id):
    game = Game()
    games[chat_id] = game
    make_telegram_request(
        "sendMessage",
        {"chat_id": chat_id, "text": game.format_grid(), "parse_mode": "Markdown"},
    )


def stop_game(chat_id):
    if chat_id in games:
        game = games[chat_id]
        make_telegram_request(
            "sendMessage",
            {"chat_id": chat_id, "text": f'Final scores:\n\n' + game.format_scores(), "parse_mode": "Markdown"},
        )
        del games[chat_id]


def make_telegram_request(method, params):
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    r = requests.post(url, data=params)
    if not r.ok:
        logging.error(r.text)


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
