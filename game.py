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

DEFAULT_GAME_LENGTH = 30
HINT_REDACTION_AMOUNT = 0.5
HINT_CHANCE = 0.33

SCRABBLE_LETTER_SCORES = {
    1: "eaionrtlsu",
    2: "dg",
    3: "bcmp",
    4: "fhvwy",
    5: "k",
    8: "jx",
    10: "qz",
}
LETTER_SCORES = {}
for score, letters in SCRABBLE_LETTER_SCORES.items():
    for letter in letters:
        LETTER_SCORES[letter] = score


class Game:
    def __init__(
        self,
        k=25,
        letters=None,
        wordlist=None,
        common_words=None,
        num_rounds=DEFAULT_GAME_LENGTH,
    ):
        self.letters = get_letters(k) if letters is None else letters
        wordlist = default_wordlist if wordlist is None else wordlist
        self.words = wordlist.possible_words(self.letters)
        self.common_words = (
            default_common_words if common_words is None else common_words
        )
        self.guesses = {}
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
        guess = guess.lower()
        if guess is None:
            return
        if guess in self.guesses:
            guesser_id = self.guesses[guess]
            guesser_name = self.players[guesser_id]
            yield f'{guesser_name} already guessed "{guess}"!', None
        elif guess in self.words:
            yield from self.register_guess(id, name, guess)
        else:
            guess = wn.morphy(guess)
            if guess in self.words:
                yield from self.register_guess(id, name, guess)

    def register_guess(self, id, name, guess):
        score = Game.word_score(guess)
        self.scores[id] += score
        self.players[id] = name
        self.words.remove(guess)
        self.remaining_rounds -= 1
        self.guesses[guess] = id
        yield self._correct_guess_message(guess, name, score)
        if self.remaining_rounds > 0:
            yield self._grid_message()

    def is_finished(self):
        return self.remaining_rounds <= 0

    def _hint_message(self):
        uncommon_words = self.words - self.common_words
        hint = random.choice([word for word in uncommon_words])
        hint_text = " ".join(redact_letters(hint, HINT_REDACTION_AMOUNT))
        hint_definition = random.choice(
            [d for d in get_definition(hint).split("\n") if hint not in d]
        )
        return f"<em>Hint: {hint_text}</em>\n{hint_definition}"

    def _final_scores_message(self):
        return f"*Final scores*\n{self._format_scores()}", "Markdown"

    def _correct_guess_message(self, guess, name, score):
        if guess in self.common_words:
            definition = ""
        else:
            definition = f"{guess.capitalize()} means:\n{get_definition(guess)}\n\n"

        return (
            f"""{name} guessed "{guess}" for {score} {"point" if score == 1 else "points"}!

{definition}*Current scores*
{self._format_scores()}""",
            "Markdown",
        )

    def _remaining_rounds_message(self):
        if self.remaining_rounds == 1:
            return "Last round!"
        else:
            return f"{self.remaining_rounds} rounds remaining!"

    def _grid_message(self):
        message = f"""<pre>{self._format_grid()}</pre>

{self._remaining_rounds_message()}"""
        if random.random() <= HINT_CHANCE:
            message += "\n" + self._hint_message()
        return (
            message,
            "HTML",
        )

    def _format_grid(self):
        grid = "\n".join(
            "  ".join(group) for group in grouper(self.letters.upper(), 5, " ")
        )
        return f"{grid}"

    def _format_scores(self):
        sorted_player_scores = sorted(
            self.scores.items(), key=itemgetter(1), reverse=True
        )
        return "\n".join(
            f"{self.players[user_id]}: {score} {'point' if score == 1 else 'points'}"
            for user_id, score in sorted_player_scores
        )

    def _longest_remaining_words(self, n=5):
        return sorted(self.words, key=len, reverse=True)[:n]

    @staticmethod
    def word_score(word):
        return sum(LETTER_SCORES[l] for l in word)

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
