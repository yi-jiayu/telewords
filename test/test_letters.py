import random

from letters import get_letters, Wordlist, redact_letters


def test_get_letters():
    n = 25
    assert len(get_letters(n)) == n


class TestWordlist:
    def test_possible_words(self):
        wordlist = Wordlist(["hat", "cat", "eat", "teat", "robot", "ttt"])
        assert wordlist.possible_words("hatcatea") == {"hat", "cat", "eat", "teat"}


def test_redact_letters():
    random.seed(1)
    assert redact_letters("colonoscopy", 0.5) == "colon____p_"
    assert redact_letters("colonoscopy", 0.75) == "_o_o_o_____"
    assert redact_letters("colonoscopy", 0.25) == "colono_c_py"
