import sqlite3 

connection = sqlite3.connect('database.db')
with open('crea_posts.sql') as f: #Apriamo il file del database
    connection.executescript(f.read()) # Eseguiamo lo script sulla connessione leggendo il database
connection.commit() # Salviamo le modifice salvate
connection.close() # Chiudiamo la connessione al db