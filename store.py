import pickle


class FileStore:
    def __init__(self, path="state.pickle"):
        self.path = path

    def load(self):
        try:
            with open(self.path, "rb") as f:
                state = pickle.load(f)
        except FileNotFoundError:
            state = {
                "games": {},
                "names": {},
            }
        return state

    def save(self, state):
        with open(self.path, "wb") as f:
            print("[start] save")
            pickle.dump(state, f)
            print("[end  ] save")
