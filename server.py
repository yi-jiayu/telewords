from sanic import Sanic
from sanic.response import json
from os import getenv
import requests

from letters import get_letters
from grid import create_grid
from game import Game

app = Sanic()
bot_token = getenv('TELEGRAM_BOT_TOKEN')
games = {}


@app.route("/", methods=['POST'])
async def test(request):
    update = request.json
    if 'message' in update and 'text' in update['message']:
        text = update['message']['text']
        handle_text(update, text)
    return json({})


def handle_text(update, text):
    chat_id = update['message']['chat']['id']
    if text.startswith('/startgame'):
        start_game(chat_id)
    elif chat_id in games:
        guesser = (update['message']['from']['id'], update['message']['from']['first_name'])
        guess(chat_id, guesser, text)


def guess(chat_id, guesser, text):
    game = games[chat_id]
    result = game.guess(guesser, text)
    if result is not False:
        print('correct guess!')
        points = result
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        requests.post(url, data={'chat_id': chat_id, 'text': f'{points} points!'})
        show_scores(chat_id)


def show_scores(chat_id):
    game = games[chat_id]
    s = ''
    for guesser, score in game.points.items():
        _, name = guesser
        s += f'{name}: {score} points\n'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    requests.post(url, data={'chat_id': chat_id, 'text': s})


def start_game(chat_id):
    game = Game(chat_id)
    games[chat_id] = game
    grid = create_grid(game.letters)
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    data = {'photo': grid.getvalue()}
    requests.post(url, files=data, data={'chat_id': chat_id})
    return json({})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
