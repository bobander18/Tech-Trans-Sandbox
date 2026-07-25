CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username text UNIQUE NOT NULL,
    password_hash text NOT NULL
);

CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY,
    title text,
    content text,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);