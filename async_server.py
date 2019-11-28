import pickle
from os import getenv

import sanic.response
from redis import Redis
from sanic import Sanic

app = Sanic()

redis = Redis()

queue_message = redis.register_script(
    """redis.call("sadd", KEYS[1], ARGV[1])
redis.call("lpush", KEYS[2], ARGV[2])"""
)


@app.route("/", methods=["POST"])
async def handle(request):
    update = request.json
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"].lower()
        chat_id = update["message"]["chat"]["id"]
        user_id = update["message"]["from"]["id"]
        name = update["message"]["from"]["first_name"]
        handle_text(chat_id, user_id, name, text)
    return sanic.response.json({})


def handle_text(chat_id, user_id, name, text):
    message = pickle.dumps((user_id, name, text))
    queue_message(keys=["unread", f"inbox:{chat_id}"], args=[chat_id, message])


if __name__ == "__main__":
    port = int(getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
