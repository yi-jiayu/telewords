import random
from collections import defaultdict
from operator import itemgetter

from more_itertools import grouper
from nltk.corpus import wordnet as wn

from dictionary import get_definition
from letters import (
    get_letters,
    default_wordlist,
    common_words as default_common_words,
    redact_letters,
)

MIN_HINT_LENGTH = 7


class Game:
    def __init__(
        self, k=25, letters=None, wordlist=None, common_words=None, num_rounds=30,
    ):
        self.letters = get_letters(k) if letters is None else letters
        wordlist = default_wordlist if wordlist is None else wordlist
        self.words = wordlist.possible_words(self.letters)
        self.common_words = (
            default_common_words if common_words is None else common_words
        )
        self.scores = defaultdict(lambda: 0)
        self.players = {}
        self.remaining_rounds = num_rounds

    def start(self):
        yield self._grid_message()

    def stop(self):
        if self.scores:
            yield self._final_scores_message()
        yield from self._missed_words_message()

    def guess(self, id, name, guess):
        guess = wn.morphy(guess.lower())
        if guess is None:
            return
        if guess in self.words:
            score = Game.word_score(guess)
            self.scores[id] += score
            self.players[id] = name
            self.words.remove(guess)
            self.remaining_rounds -= 1
            yield self._correct_guess_message(guess, name, score)
            if self.remaining_rounds > 0:
                yield self._grid_message()

    def _final_scores_message(self):
        return f"*Final scores*\n{self.format_scores()}", "Markdown"

    def _correct_guess_message(self, guess, name, score):
        if guess in self.common_words:
            definition = ""
        else:
            definition = f"{guess.capitalize()} means:\n{get_definition(guess)}\n\n"

        return (
            f"""{name} guessed "{guess}" for {score} {"point" if score == 1 else "points"}!

{definition}*Current scores*
{self.format_scores()}""",
            "Markdown",
        )

    def _remaining_rounds_message(self):
        if self.remaining_rounds == 1:
            return "Last round!"
        else:
            return f"{self.remaining_rounds} rounds remaining!"

    def _grid_message(self):
        return (
            f"""<pre>{self.format_grid()}</pre>
<em>Hint: {self.get_hint()}</em>

{self._remaining_rounds_message()}""",
            "HTML",
        )

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

    def _longest_remaining_words(self, n=5):
        return sorted(self.words, key=len, reverse=True)[:n]

    def get_hint(self):
        uncommon_words = self.words - self.common_words
        hint = redact_letters(
            random.choice(
                [word for word in uncommon_words if len(word) > MIN_HINT_LENGTH]
            )
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

    def _missed_words_message(self):
        remaining_words = self._longest_remaining_words()
        if not remaining_words:
            return
        message = "Here are some words you missed:"
        for word in remaining_words:
            definition = get_definition(word)
            if definition:
                word += "\n" + definition
            message += "\n\n" + word
        yield message, None
