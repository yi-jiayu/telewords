import random
from collections import Counter

from nltk.corpus import wordnet as wn

alphabet = "abcdefghijklmnopqrstuvwxyz"
weights = (
    0.08463264442962931,
    0.018259030660157567,
    0.04379076252535897,
    0.03236198627927482,
    0.1077990207674717,
    0.011191351785343053,
    0.023619145931453724,
    0.026417485680695643,
    0.08963633626529603,
    0.0015441192283705027,
    0.007643748611081242,
    0.05580134339806591,
    0.030084374574363606,
    0.07202018681405335,
    0.07199954120877151,
    0.03249618271360674,
    0.0016725807723463586,
    0.0704815157315211,
    0.07164971289705155,
    0.0660954715872026,
    0.037613425378323545,
    0.009449952328723915,
    0.006371463185588221,
    0.00298013577352918,
    0.020174484039083278,
    0.004213997433636566,
)


class Wordlist:
    def __init__(self, words):
        self.letter_counts = {word: Counter(word) for word in words}

    def _possible_words_generator(self, letters):
        available_letters = Counter(letters)
        for word, letter_count in self.letter_counts.items():
            if all(
                available_letters.get(letter, 0) >= count
                for letter, count in letter_count.items()
            ):
                yield word

    def possible_words(self, letters):
        return set(self._possible_words_generator(letters))


default_wordlist = Wordlist(wn.all_lemma_names())


def get_letters(k):
    return "".join(random.choices(alphabet, weights, k=k))


if __name__ == "__main__":
    letters = get_letters(25)
    print(letters)
    words = default_wordlist.possible_words(letters)
    print(words)
    print(len(words))
