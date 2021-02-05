import sys
from nltk.corpus import wordnet as wn

if __name__ == "__main__":
    letters = sys.argv[1]
    words = [
        w
        for w in wn.all_lemma_names()
        if 4 <= len(w) and set(w).issubset(set(letters)) and letters[3] in w
    ]
    words = sorted(words, key=lambda w: (len(w), w))
    for word in words:
        print(word)
