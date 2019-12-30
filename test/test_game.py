import re

from game import (
    Game,
    DEFAULT_GAME_LENGTH,
    get_player_name,
    redis,
    get_leaderboard_scores,
    format_scores,
    set_player_name,
)
from helpers import random_seed, regex_matcher


class TestGame:
    def setup_method(self):
        redis.flushdb()

    @random_seed(3)
    def test_game_start(self):
        game = Game("")
        assert game.start() == (
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
        )

    @random_seed(1)
    def test_guesses(self):
        game = Game("")
        game.start()
        assert game.guess(1, "Player 1", "locus") == (
            regex_matcher(
                fr"""Player 1 guessed "locus" for 7 points!

<strong>Current scores</strong>
Player 1: 7 points

<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

{DEFAULT_GAME_LENGTH - 1} rounds remaining!(

<em>Hint: [a-z_ ]+<\/em>\n\([ansv]\) [^\n]+)?"""
            ),
            "HTML",
        )
        assert game.guess(1, "Player 1", "wrong guess") is None
        message, parse_mode = game.guess(2, "Player 2", "trackable")
        assert re.match(
            fr"""Player 2 guessed "trackable" for 17 points!

Trackable means:
\(a\) capable of being traced or tracked

<strong>Current scores</strong>
Player 2: 17 points
Player 1: 7 points

<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

{DEFAULT_GAME_LENGTH - 2} rounds remaining!(

<em>Hint: [a-z_ ]+<\/em>\n\([ansv]\) [^\n]+)?""",
            message,
        )
        assert parse_mode == "HTML"

        assert game.guess(1, "Player 1", "trackable") == (
            'Player 2 already guessed "trackable"!',
            None,
        )

    @random_seed(1)
    def test_last_round(self):
        game = Game("", num_rounds=2)
        assert game.guess(1, "Player 1", "locus") == (
            regex_matcher(
                r"""Player 1 guessed "locus" for 7 points!

<strong>Current scores</strong>
Player 1: 7 points

<pre>C  S  R  E  L
L  O  S  B  A
S  I  R  A  K
R  E  U  T  A
A  N  U  I  E</pre>

Last round!(

<em>Hint: [a-z_ ]+<\/em>\n\([ansv]\) [^\n]+)?"""
            ),
            "HTML",
        )
        assert game.guess(2, "Player 2", "trackable") == (
            """Player 2 guessed "trackable" for 17 points!

Trackable means:
(a) capable of being traced or tracked

<strong>Current scores</strong>
Player 2: 17 points
Player 1: 7 points""",
            "HTML",
        )

    @random_seed(1)
    def test_game_stop(self):
        game = Game("chat_id")
        game.guess(1, "Player 1", "locus")
        game.guess(2, "Player 2", "lentibulariaceae")
        assert game.stop() == (
            regex_matcher(
                r"""\*Final scores\*
Player 2: 20 points
Player 1: 7 points

Here are some words you missed:\n\n([a-z]+\n(\([ansv]\) .+\n?)+\n?)"""
            ),
            "Markdown",
        )
        assert get_player_name(1) == "Player 1"
        assert get_player_name(2) == "Player 2"
        assert get_leaderboard_scores("chat_id") == {"1": 7, "2": 20}

    @random_seed(1)
    def test_game_stop_without_participation(self):
        game = Game("")
        message, parse_mode = game.stop()
        assert re.match(
            r"Here are some words you missed:\n\n([a-z]+\n(\([ansv]\) .+\n?)+\n?)",
            message,
        )
        assert parse_mode == "Markdown"

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


def test_format_scores():
    set_player_name(1, "Player 1")
    set_player_name(2, "Player 2")
    scores = {1: 1, 2: 2}
    assert format_scores(scores) == "Player 2: 2 points\nPlayer 1: 1 points"
