from letters import get_letters, default_wordlist

states = {}


class Game:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.letters = get_letters(25)
        self.words = default_wordlist.possible_words(self.letters)
        self.points = {}

    def guess(self, guesser, word):
        if word in self.words:
            self.points[guesser] = self.points.get(guesser, 0) + len(word)
            self.words.remove(word)
            return len(word)
        return False


def start_game(chat_id):
    states[chat_id] = Game(chat_id)
    return states[chat_id]
