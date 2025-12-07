-- NeoRadio PostgreSQL Database Initialization Script

-- Create songs table
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    year TEXT,
    UNIQUE(title, artist)
);

-- Create ratings table
CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK(rating IN (1, -1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(song_id, user_id),
    FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ratings_song_id ON ratings(song_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist);
CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
