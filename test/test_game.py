from game import *
from letters import Wordlist


class TestGame:
    def test_successful_guess(self):
        wordlist = Wordlist(["hat", "cat", "eat", "teat"])
        letters = "hatcatea"
        game = Game(letters=letters, wordlist=wordlist)
        correct_guess = "hat"
        assert game.make_guess("player", correct_guess) == Game.word_score(
            correct_guess
        )

    def test_unsuccessful_guess(self):
        wordlist = Wordlist(["hat", "cat", "eat", "teat"])
        letters = "hatcatea"
        game = Game(letters=letters, wordlist=wordlist)
        wrong_guess = "ttt"
        assert game.make_guess("player", wrong_guess) is None
