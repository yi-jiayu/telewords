import json
import sqlite3

with open('dictionary_compact.json') as f:
    data = json.load(f)

conn = sqlite3.connect('dictonary.sqlite')

with conn:
    conn.execute('drop table if exists words')

with conn:
    conn.execute('create table words (word text, definition text)')

count = 0
with conn:
    for word, definition in data.items():
        conn.execute('insert into words values (?, ?)', (word, definition))
        count += 1

print('inserted', count, 'words')

with conn:
    conn.execute('create index words_word_index on words (word)')
