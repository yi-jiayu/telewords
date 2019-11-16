from game import *
from letters import Wordlist


class TestGame:
    def test_format_grid(self):
        game = Game(letters="abcdefghijklmnopqrstuvwxy")
        assert (
            game.format_grid()
            == """```
A  B  C  D  E
F  G  H  I  J
K  L  M  N  O
P  Q  R  S  T
U  V  W  X  Y
```"""
        )

    def test_format_scores(self):
        wordlist = Wordlist(["hat", "cat", "eat", "teat"])
        letters = "hatcatea"
        game = Game(letters=letters, wordlist=wordlist)
        game.make_guess(1, "Player 1", "hat")
        game.make_guess(2, "Player 2", "cat")
        game.make_guess(2, "Player 2", "eat")
        assert (
            game.format_scores()
            == """Player 2: 2 points
Player 1: 1 point"""
        )

    def test_successful_guess(self):
        wordlist = Wordlist(["hat", "cat", "eat", "teat"])
        letters = "hatcatea"
        game = Game(letters=letters, wordlist=wordlist)
        correct_guess = "hat"
        assert game.make_guess(1, "Player 1", correct_guess) == Game.word_score(
            correct_guess
        )

    def test_unsuccessful_guess(self):
        wordlist = Wordlist(["hat", "cat", "eat", "teat"])
        letters = "hatcatea"
        game = Game(letters=letters, wordlist=wordlist)
        wrong_guess = "ttt"
        assert game.make_guess(1, "Player 1", wrong_guess) is None

    def test_longest_remaining_words(self):
        wordlist = Wordlist(["hat", "cat", "predator", "conversation"])
        letters = "hatcatpredatorconversation"
        game = Game(letters=letters, wordlist=wordlist)
        game.make_guess(1, "Player 1", "hat")
        assert game.longest_remaining_words() == ["conversation", "predator", "cat"]
