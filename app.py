import atexit
from os import getenv

from flask import Flask, jsonify, request
from nltk.corpus import wordnet as wn

import game
from store import FileStore

app = Flask(__name__)

bot_token = getenv("TELEGRAM_BOT_TOKEN")
bot_name = getenv("TELEGRAM_BOT_USERNAME")

state_file = "state.pickle"

store = FileStore()
state = store.load()
atexit.register(lambda: store.save(state))


@app.route("/readyz", methods=["GET"])
def readyz():
    return "ready", 200


@app.route("/updates", methods=["POST"])
def handle_update():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        return handle_text(update, text)
    return "", 204


def handle_text(update, text):
    chat_id = update["message"]["chat"]["id"]
    if "start" in text and (chat_id > 0 or bot_name.lower() in text.lower()):
        return start_game(chat_id)
    else:
        sender = update["message"]["from"]
        return continue_game(chat_id, sender, text)


def start_game(chat_id):
    letters, words = game.new_game()
    state["games"][chat_id] = {
        "letters": letters,
        "remaining_words": words,
        "discovered_words": set(),
        "scores": {},
    }
    return jsonify(
        {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": f"<pre>{game.format(letters)}</pre>\n\n0/{len(words)} words found",
            "parse_mode": "HTML",
        }
    )


def format_scores(scores, names):
    lines = []
    for user_id, points in scores.items():
        name = names[user_id]
        lines.append(f'{name}: {points} {"point" if points == 1 else "points"}')
    return "\n".join(lines)


def continue_game(chat_id, sender, text: str):
    if chat_id not in state["games"]:
        return "", 204
    if len(text) > 7 or not text.isalpha():
        return "", 204
    g = state["games"][chat_id]
    text = text.lower()
    if text in g["remaining_words"]:
        user_id = sender["id"]
        name = sender["first_name"]
        state["names"][user_id] = name
        points = game.score(text)
        g["scores"][user_id] = g["scores"].get(user_id, 0) + points
        g["discovered_words"].add(text)
        g["remaining_words"].remove(text)
        num_discovered_words = len(g["discovered_words"])
        num_words = len(g["discovered_words"]) + len(g["remaining_words"])
        lemmas = wn.lemmas(text)
        if len(lemmas) == 1:
            definition = f'<em>{lemmas[0].synset().definition()}</em>\n'
        else:
            definition = ""
        return jsonify(
            {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": f"""{state['names'][user_id]} guessed "{text}" for {points} {'point' if points == 1 else 'points'}!
{definition}
<pre>{game.format(g['letters'])}</pre>

{num_discovered_words}/{num_words} words found

{format_scores(g['scores'], state['names'])}""",
                "parse_mode": "HTML",
            }
        )
    return "", 204
