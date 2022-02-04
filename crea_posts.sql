DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS accounts;



CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    info TEXT,
    today TEXT,
    id_acc INTEGER
);

CREATE TABLE accounts (
    email TEXT,
    username TEXT,
    passw VARCHAR,
    id_acc INTEGER PRIMARY KEY AUTOINCREMENT
);

