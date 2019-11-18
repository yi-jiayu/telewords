import random
from collections import defaultdict
from operator import itemgetter

from more_itertools import grouper
from nltk.corpus import wordnet as wn

from letters import get_letters, default_wordlist, common_words, redact_letters

states = {}


class Game:
    def __init__(
        self,
        k=25,
        letters=None,
        wordlist=None,
        num_rounds=30,
        common_words=common_words,
    ):
        self.letters = get_letters(k) if letters is None else letters
        wordlist = default_wordlist if wordlist is None else wordlist
        self.words = wordlist.possible_words(self.letters)
        self.common_words = common_words
        self.scores = defaultdict(lambda: 0)
        self.players = {}
        self.remaining_rounds = num_rounds

    def is_finished(self):
        return self.remaining_rounds <= 0

    def format_grid(self):
        grid = "\n".join(
            "  ".join(group) for group in grouper(self.letters.upper(), 5, " ")
        )
        return f"{grid}"

    def format_scores(self):
        sorted_player_scores = sorted(
            self.scores.items(), key=itemgetter(1), reverse=True
        )
        return "\n".join(
            f"{self.players[user_id]}: {score} {'point' if score == 1 else 'points'}"
            for user_id, score in sorted_player_scores
        )

    def longest_remaining_words(self, n=5):
        return sorted(self.words, key=len, reverse=True)[:n]

    def make_guess(self, user_id, name, guess):
        guess = wn.morphy(guess)
        if guess is None:
            return
        if guess in self.words:
            score = Game.word_score(guess)
            self.scores[user_id] += score
            self.players[user_id] = name
            self.words.remove(guess)
            self.remaining_rounds -= 1
            return guess, score

    def get_hint(self):
        uncommon_words = self.words - self.common_words
        hint = redact_letters(
            random.choice([word for word in uncommon_words if len(word) > 7]), 0.3
        )
        return " ".join(hint)

    @staticmethod
    def word_score(word):
        length = len(word)
        if length <= 5:
            return 1
        elif length <= 7:
            return 2
        elif length <= 11:
            return 4
        else:
            return 9


def start_game(chat_id):
    states[chat_id] = Game(chat_id)
    return states[chat_id]
