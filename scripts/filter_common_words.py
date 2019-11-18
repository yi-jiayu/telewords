import sys

from nltk.corpus import wordnet as wn

common_words = set()
for line in sys.stdin:
    line = line.strip()
    if len(line) >= 4 and line.isalpha():
        normalised = wn.morphy(line)
        if normalised and len(normalised) >= 4:
            common_words.add(normalised)

for word in common_words:
    print(word)
