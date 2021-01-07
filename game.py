import random

from nltk.corpus import wordnet as wn

alphabet = "abcdefghijklmnopqrstuvwxyz"


def new_game():
    attempts = 0
    while True:
        attempts += 1
        letters = random.sample(alphabet, 7)
        words = {
            w
            for w in wn.all_lemma_names()
            if 4 <= len(w) <= 7 and set(w).issubset(set(letters)) and letters[3] in w
        }
        for word in words:
            if set(word) == set(letters):
                print("Pangram:", word)
                print("Generation attempts:", attempts)
                print("Number of words:", len(words))
                return letters, words


def format(letters: str):
    a, b, c, d, e, f, g = "".join(letters).upper()
    return f""" {a} {b}
{c} {d} {e}
 {f} {g}"""


def score(word):
    return len(word) - 3


if __name__ == "__main__":
    letters, words = new_game()
    print(letters)
    for w in words:
        lemmas = wn.lemmas(w)
        print(w, ":", lemmas[0].synset().definition())
