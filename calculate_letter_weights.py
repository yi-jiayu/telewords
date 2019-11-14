total_count = 0
frequencies = {}
with open("letter_frequencies.txt") as f:
    for line in f:
        freq, letter = line.strip().split()
        freq = int(freq)
        frequencies[letter] = freq
        total_count += freq
weights = {letter: freq / total_count for letter, freq in frequencies.items()}
print("".join(letter for letter, _ in sorted(weights.items())))
print(tuple(weight for _, weight in sorted(weights.items())))
