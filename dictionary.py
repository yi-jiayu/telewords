import sqlite3

conn = sqlite3.connect("dictionary.sqlite")


def get_definition(word):
    c = conn.cursor()
    c.execute("select definition from words where word = ?", (word,))
    row = c.fetchone()
    if row is not None:
        return summarise(row[0])


def summarise(definition):
    return "\n\n".join(
        line if len(line) <= 100 else line[:100] + "..."
        for line in definition.split("\n\n")
    )
