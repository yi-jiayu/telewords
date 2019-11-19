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
<em>Hint: _ r o _ i n a _ _</em>

30 rounds remaining!""",
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
<em>Hint: c o _ _ s e _ _ _ s</em>

29 rounds remaining!""",
                "HTML",
            ),
        ]
        assert list(game.guess(1, "Player 1", "wrong guess")) == []
        assert list(game.guess(2, "Player 2", "trackable")) == [
            (
                """Player 2 guessed "trackable" for 4 points!

Trackable means:
(a) capable of being traced or tracked

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
<em>Hint: _ _ _ _ n i s e</em>

28 rounds remaining!""",
                "HTML",
            ),
        ]

    @random_seed(1)
    def test_last_round(self):
        game = Game(num_rounds=2)
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
<em>Hint: _ r o _ i n a _ _</em>

Last round!""",
                "HTML",
            ),
        ]
        assert list(game.guess(2, "Player 2", "trackable")) == [
            (
                """Player 2 guessed "trackable" for 4 points!

Trackable means:
(a) capable of being traced or tracked

*Current scores*
Player 2: 4 points
Player 1: 1 point""",
                "Markdown",
            ),
        ]

    @random_seed(1)
    def test_game_stop(self):
        game = Game()
        list(game.guess(1, "Player 1", "locus"))
        list(game.guess(2, "Player 2", "lentibulariaceae"))
        assert list(game.stop()) == [
            (
                """*Final scores*
Player 2: 9 points
Player 1: 1 point""",
                "Markdown",
            ),
            (
                """Here are some words you missed:

auriculariales
(n) coextensive with the family Auriculariaceae; sometimes included in the order Tremellales

irresoluteness
(n) the trait of being irresolute; lacking firmness of purpose

secularisation
(n) the activity of changing something (art or education or society or morality etc.) so it is no longer under the control or influence of religion
(n) transfer of property from ecclesiastical to civil possession

rebelliousness
(n) intentionally contemptuous behavior or attitude
(n) an insubordinate act

subterraneous
(s) being or operating under the surface of the earth
(s) lying beyond what is openly revealed or avowed (especially being kept in the background or deliberately concealed); ; - Bertrand Russell""",
                None,
            ),
        ]

    @random_seed(1)
    def test_game_stop_without_participation(self):
        game = Game()
        assert list(game.stop()) == [
            (
                """Here are some words you missed:

lentibulariaceae
(n) carnivorous aquatic or bog plants: genera Utricularia, Pinguicula, and Genlisea

auriculariales
(n) coextensive with the family Auriculariaceae; sometimes included in the order Tremellales

irresoluteness
(n) the trait of being irresolute; lacking firmness of purpose

secularisation
(n) the activity of changing something (art or education or society or morality etc.) so it is no longer under the control or influence of religion
(n) transfer of property from ecclesiastical to civil possession

rebelliousness
(n) intentionally contemptuous behavior or attitude
(n) an insubordinate act""",
                None,
            )
        ]

    def test_format_grid(self):
        game = Game(letters="abcdefghijklmnopqrstuvwxy")
        assert (
            game._format_grid()
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
