from collections import defaultdict

from letters import get_letters, default_wordlist

states = {}


class Game:
    def __init__(self, k=25, letters=None, wordlist=None):
        self.letters = get_letters(k) if letters is None else letters
        wordlist = default_wordlist if wordlist is None else wordlist
        self.words = wordlist.possible_words(self.letters)
        self.scores = defaultdict(lambda: 0)

    def make_guess(self, guesser, guess):
        if guess in self.words:
            score = Game.word_score(guess)
            self.scores[guesser] += score
            self.words.remove(guess)
            return score

    @staticmethod
    def word_score(word):
        return len(word)


def start_game(chat_id):
    states[chat_id] = Game(chat_id)
    return states[chat_id]
