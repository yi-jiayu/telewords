from letters import *


def test_get_letters():
    n = 25
    assert len(get_letters(n)) == n


class TestWordlist:
    def test_possible_words(self):
        wordlist = Wordlist(["hat", "cat", "eat", "teat", "robot", "ttt"])
        assert wordlist.possible_words("hatcatea") == {"hat", "cat", "eat", "teat"}
