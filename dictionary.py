from nltk.corpus import wordnet as wn


def get_definition(word):
    synsets = wn.synsets(word)
    if synsets:
        return "\n".join(f"({s.pos()}) {s.definition()}" for s in synsets)
