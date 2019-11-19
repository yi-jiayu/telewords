from game import Game
from helpers import random_seed
from letters import Wordlist


class TestGame:
    @random_seed(1)
    def test_game_start(self):
        game = Game()
        assert list(game.start()) == [
            (
                """<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

<em>Hint: _ r o _ i n a _ _</em>""",
                "HTML",
            )
        ]

    @random_seed(1)
    def test_correct_guesses(self):
        game = Game()
        list(game.start())
        assert list(game.guess(1, "Player 1", "locus")) == [
            (
                """Player 1 guessed "locus" for 1 point!

*Current scores*
Player 1: 1 point""",
                "Markdown",
            ),
            (
                """<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

<em>Hint: c o _ _ s e _ _ _ s</em>""",
                "HTML",
            ),
        ]
        assert list(game.guess(2, "Player 2", "trackable")) == [
            (
                """Player 2 guessed "trackable" for 4 points!

*Current scores*
Player 2: 4 points
Player 1: 1 point""",
                "Markdown",
            ),
            (
                """<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

<em>Hint: _ _ _ _ n i s e</em>""",
                "HTML",
            ),
        ]

    def test_format_grid(self):
        game = Game(letters="abcdefghijklmnopqrstuvwxy")
        assert (
            game.format_grid()
            == """A  B  C  D  E
F  G  H  I  J
K  L  M  N  O
P  Q  R  S  T
U  V  W  X  Y"""
        )

    @random_seed(1)
    def test_get_hint(self):
        game = Game(
            letters="hcatlongword",
            wordlist=Wordlist(["hat", "cat", "longword"]),
            common_words=frozenset(["hat"]),
        )
        assert game.get_hint() == "l o n g _ _ _ _"
