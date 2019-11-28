import asyncio
import logging
import pickle
from enum import Enum
from os import getenv

import httpx
import sentry_sdk
from redis import Redis

from game import Game, get_leaderboard_scores, format_scores


class Command(Enum):
    START = 1
    STOP = 2


MIN_DELAY = 2

redis = Redis()
bot_token = getenv("TELEGRAM_BOT_TOKEN")
bot_name = getenv("TELEGRAM_BOT_USERNAME").lower()

get_messages = redis.register_script(
    """redis.replicate_commands()

local min_delay = tonumber(ARGV[1])

local now = redis.call("time")[1]
local cursor = "0"
repeat
    local result = redis.call("sscan", "unread", cursor)
    cursor = result[1]
    local chat_ids = result[2]
    for _, chat_id in ipairs(chat_ids) do
        local prev = redis.call("get", "prev:" .. chat_id)
        if prev == false or now - tonumber(prev) > min_delay then
            local inbox = "inbox:" .. chat_id
            local messages = redis.call("lrange", inbox, 0, -1)
            redis.call("del", inbox)
            redis.call("set", "prev:" .. chat_id, now)
            redis.call("srem", "unread", chat_id)
            return { chat_id, messages }
        end
    end
until cursor == "0"
return false
"""
)


def is_start_message(chat_id, text):
    return "/start" in text and (chat_id > 0 or bot_name in text)


def is_stop_message(chat_id, text):
    return "/stop" in text and (chat_id > 0 or bot_name in text)


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
    await asyncio.gather(*replies)


def handle_messages(chat_id, messages):
    guesses = []
    command = None
    while messages:
        user_id, name, text = messages.pop()
        if is_start_message(chat_id, text):
            command = Command.START
            break
        elif is_stop_message(chat_id, text):
            command = Command.STOP
            break
        else:
            guesses.append((user_id, name, text))

    game = Game.find(chat_id)
    if game:
        replies = game.batch_guess(guesses)
        if game.is_finished():
            replies.extend(game.stop())
            scores = get_leaderboard_scores(chat_id)
            replies.append((f"*All-time scores*\n{format_scores(scores)}", "Markdown"))
            game.delete()
        else:
            game.save()
        asyncio.create_task(transduce(chat_id, replies))

    if command == Command.START:
        game = Game(chat_id)
        replies = game.start()
        game.save()
        asyncio.create_task(transduce(chat_id, replies))
    elif command == Command.STOP:
        if game is None:
            asyncio.create_task(
                send_message(
                    chat_id,
                    f"No game in progress! To start a new game, tag {bot_name} and say start!",
                )
            )
        else:
            replies = game.stop()
            game.delete()
            scores = get_leaderboard_scores(chat_id)
            replies.append((f"*All-time scores*\n{format_scores(scores)}", "Markdown"))
            asyncio.create_task(transduce(chat_id, replies))


async def poll():
    while True:
        messages = get_messages(args=[MIN_DELAY])
        if messages is None:
            await asyncio.sleep(1)
            continue

        chat_id, messages = messages
        chat_id = int(chat_id.decode())
        messages = [pickle.loads(m) for m in messages]

        try:
            handle_messages(chat_id, messages)
        except Exception as e:
            print(e)


def main():
    asyncio.run(poll())


if __name__ == "__main__":
    sentry_sdk.init()
    main()
