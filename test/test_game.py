from game import Game, DEFAULT_GAME_LENGTH
from helpers import random_seed, regex_matcher


class TestGame:
    @random_seed(3)
    def test_game_start(self):
        game = Game("")
        assert list(game.start()) == [
            (
                regex_matcher(
                    fr"""<pre>[A-Z]  [A-Z]  [A-Z]  [A-Z]  [A-Z]
[A-Z]  [A-Z]  [A-Z]  [A-Z]  [A-Z]
[A-Z]  [A-Z]  [A-Z]  [A-Z]  [A-Z]
[A-Z]  [A-Z]  [A-Z]  [A-Z]  [A-Z]
[A-Z]  [A-Z]  [A-Z]  [A-Z]  [A-Z]</pre>

{DEFAULT_GAME_LENGTH} rounds remaining!(

<em>Hint: [a-z_ ]+<\/em>\n\([ansv]\) [^\n]+)?"""
                ),
                "HTML",
            ),
        ]

    @random_seed(1)
    def test_guesses(self):
        game = Game("")
        list(game.start())
        assert list(game.guess(1, "Player 1", "locus")) == [
            (
                """Player 1 guessed "locus" for 7 points!

*Current scores*
Player 1: 7 points""",
                "Markdown",
            ),
            (
                regex_matcher(
                    fr"""<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

{DEFAULT_GAME_LENGTH - 1} rounds remaining!(

<em>Hint: [a-z_ ]+<\/em>\n\([ansv]\) [^\n]+)?"""
                ),
                "HTML",
            ),
        ]
        assert list(game.guess(1, "Player 1", "wrong guess")) == []
        assert list(game.guess(2, "Player 2", "trackable")) == [
            (
                """Player 2 guessed "trackable" for 17 points!

Trackable means:
(a) capable of being traced or tracked

*Current scores*
Player 2: 17 points
Player 1: 7 points""",
                "Markdown",
            ),
            (
                regex_matcher(
                    fr"""<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

{DEFAULT_GAME_LENGTH - 2} rounds remaining!(

<em>Hint: [a-z_ ]+<\/em>\n\([ansv]\) [^\n]+)?"""
                ),
                "HTML",
            ),
        ]
        assert list(game.guess(1, "Player 1", "trackable")) == [
            ('Player 2 already guessed "trackable"!', None)
        ]

    @random_seed(1)
    def test_last_round(self):
        game = Game("", num_rounds=2)
        assert list(game.guess(1, "Player 1", "locus")) == [
            (
                """Player 1 guessed "locus" for 7 points!

*Current scores*
Player 1: 7 points""",
                "Markdown",
            ),
            (
                regex_matcher(
                    r"""<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

Last round!(

<em>Hint: [a-z_ ]+<\/em>\n\([ansv]\) [^\n]+)?"""
                ),
                "HTML",
            ),
        ]
        assert list(game.guess(2, "Player 2", "trackable")) == [
            (
                """Player 2 guessed "trackable" for 17 points!

Trackable means:
(a) capable of being traced or tracked

*Current scores*
Player 2: 17 points
Player 1: 7 points""",
                "Markdown",
            ),
        ]

    @random_seed(1)
    def test_game_stop(self):
        game = Game("")
        list(game.guess(1, "Player 1", "locus"))
        list(game.guess(2, "Player 2", "lentibulariaceae"))
        assert list(game.stop()) == [
            (
                """*Final scores*
Player 2: 20 points
Player 1: 7 points""",
                "Markdown",
            ),
            (
                regex_matcher(
                    r"Here are some words you missed:\n\n([a-z]+\n(\([ansv]\) .+\n?)+\n?)"
                ),
                None,
            ),
        ]

    @random_seed(1)
    def test_game_stop_without_participation(self):
        game = Game("")
        assert list(game.stop()) == [
            (
                regex_matcher(
                    r"Here are some words you missed:\n\n([a-z]+\n(\([ansv]\) .+\n?)+\n?)"
                ),
                None,
            )
        ]

    def test_format_grid(self):
        game = Game("", letters="abcdefghijklmnopqrstuvwxy")
        assert (
            game._format_grid()
            == """A  B  C  D  E
F  G  H  I  J
K  L  M  N  O
P  Q  R  S  T
U  V  W  X  Y"""
        )

    def test_save_load(self):
        id = "game"
        game = Game(id)
        game.save()
        loaded = Game.find(id)
        assert game.letters == loaded.letters
        assert game.words == loaded.words
