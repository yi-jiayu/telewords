from os import getenv
import json

import requests
from sanic import Sanic
import sanic.response

from game import Game
from grid import create_grid, grid_to_video

app = Sanic()
bot_token = getenv("TELEGRAM_BOT_TOKEN")
base_url = getenv("HOST")
games = {}

app.static("assets", "assets")
app.static("pip.html", "pip.html")


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
    elif chat_id in games:
        guesser = (
            update["message"]["from"]["id"],
            update["message"]["from"]["first_name"],
        )
        guess(chat_id, guesser, text)


def guess(chat_id, guesser, text):
    game = games[chat_id]
    result = game.guess(guesser, text)
    if result is not False:
        print("correct guess!")
        points = result
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(
            url, data={"chat_id": chat_id, "text": f"{text}: {points} points!"}
        )
        show_scores(chat_id)


def show_scores(chat_id):
    game = games[chat_id]
    s = ""
    for guesser, score in game.points.items():
        _, name = guesser
        s += f"{name}: {score} points\n"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": s})


def start_game(chat_id):
    game = Game(chat_id)
    games[chat_id] = game
    grid = create_grid(game.letters)
    with open(f"assets/{game.letters}.mp4", "wb") as f:
        grid_to_video(grid, f)
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {"photo": grid}
    data = {
        "chat_id": chat_id,
        "reply_markup": json.dumps(
            {
                "inline_keyboard": [
                    [
                        {
                            "text": "Open overlay",
                            "url": f"https://{base_url}/pip.html#{game.letters}",
                        }
                    ]
                ]
            }
        ),
    }
    requests.post(url, files=files, data=data)


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
