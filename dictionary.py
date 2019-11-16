import sqlite3

conn = sqlite3.connect('dictionary.sqlite')


def get_definition(word):
    c = conn.cursor()
    c.execute('select definition from words where word = ?', (word,))
    row = c.fetchone()
    if row is not None:
        return row[0]
