from collections import defaultdict

from more_itertools import grouper
from operator import itemgetter
from typing import Tuple

from letters import get_letters, default_wordlist

states = {}


class Game:
    def __init__(self, k=25, letters=None, wordlist=None):
        self.letters = get_letters(k) if letters is None else letters
        wordlist = default_wordlist if wordlist is None else wordlist
        self.words = wordlist.possible_words(self.letters)
        self.scores = defaultdict(lambda: 0)
        self.players = {}

    def format_grid(self):
        return (
                "```\n"
                + "\n".join(
            "  ".join(group) for group in grouper(self.letters.upper(), 5, " ")
        )
                + "\n```"
        )

    def format_scores(self):
        sorted_player_scores = sorted(
            self.scores.items(), key=itemgetter(1), reverse=True
        )
        return "\n".join(
            f"{self.players[user_id]}: {score} points"
            for user_id, score in sorted_player_scores
        )

    def make_guess(self, user_id, name, guess):
        if guess in self.words:
            score = Game.word_score(guess)
            self.scores[user_id] += score
            self.players[user_id] = name
            self.words.remove(guess)
            return score

    @staticmethod
    def word_score(word):
        length = len(word)
        if length < 7:
            return 1
        elif length < 9:
            return 4
        elif length < 11:
            return 9
        else:
            return 16


def start_game(chat_id):
    states[chat_id] = Game(chat_id)
    return states[chat_id]
