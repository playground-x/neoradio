"""
Tests for database operations and schema.
"""

import pytest
import sqlite3
from app import get_db_connection, DATABASE


class TestDatabaseSchema:
    """Tests for database schema and initialization."""

    def test_songs_table_exists(self, test_app):
        """Test that the songs table is created."""
        conn = get_db_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='songs'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None

    def test_ratings_table_exists(self, test_app):
        """Test that the ratings table is created."""
        conn = get_db_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ratings'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None

    def test_songs_table_schema(self, test_app):
        """Test that the songs table has correct columns."""
        conn = get_db_connection()
        cursor = conn.execute("PRAGMA table_info(songs)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        expected_columns = {'id', 'title', 'artist', 'album', 'year'}
        assert expected_columns.issubset(columns)

    def test_ratings_table_schema(self, test_app):
        """Test that the ratings table has correct columns."""
        conn = get_db_connection()
        cursor = conn.execute("PRAGMA table_info(ratings)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        expected_columns = {'id', 'song_id', 'user_id', 'rating', 'created_at'}
        assert expected_columns.issubset(columns)


class TestDatabaseConstraints:
    """Tests for database constraints and data integrity."""

    def test_songs_unique_constraint(self, test_app):
        """Test that songs have unique (title, artist) constraint."""
        conn = get_db_connection()

        # Insert first song
        conn.execute(
            "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
            ('Unique Song', 'Unique Artist', 'Album', '2025')
        )
        conn.commit()

        # Try to insert duplicate
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
                ('Unique Song', 'Unique Artist', 'Different Album', '2024')
            )
            conn.commit()

        conn.close()

    def test_ratings_unique_constraint(self, test_app):
        """Test that ratings have unique (song_id, user_id) constraint."""
        conn = get_db_connection()

        # Create a song
        conn.execute(
            "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
            ('Rating Test', 'Artist', 'Album', '2025')
        )
        conn.commit()

        song = conn.execute(
            "SELECT id FROM songs WHERE title = ?",
            ('Rating Test',)
        ).fetchone()
        song_id = song[0]

        # Insert first rating
        conn.execute(
            "INSERT INTO ratings (song_id, user_id, rating) VALUES (?, ?, ?)",
            (song_id, 'test_user', 1)
        )
        conn.commit()

        # Try to insert duplicate rating from same user
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO ratings (song_id, user_id, rating) VALUES (?, ?, ?)",
                (song_id, 'test_user', -1)
            )
            conn.commit()

        conn.close()

    def test_rating_value_constraint(self, test_app):
        """Test that rating values must be 1 or -1."""
        conn = get_db_connection()

        # Create a song
        conn.execute(
            "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
            ('Rating Value Test', 'Artist', 'Album', '2025')
        )
        conn.commit()

        song = conn.execute(
            "SELECT id FROM songs WHERE title = ?",
            ('Rating Value Test',)
        ).fetchone()
        song_id = song[0]

        # Try invalid rating value
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO ratings (song_id, user_id, rating) VALUES (?, ?, ?)",
                (song_id, 'test_user', 5)
            )
            conn.commit()

        conn.close()


class TestDatabaseOperations:
    """Tests for database CRUD operations."""

    def test_insert_song(self, test_app):
        """Test inserting a song into the database."""
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
            ('Insert Test', 'Test Artist', 'Test Album', '2025')
        )
        conn.commit()

        song = conn.execute(
            "SELECT * FROM songs WHERE title = ?",
            ('Insert Test',)
        ).fetchone()

        conn.close()

        assert song is not None
        assert song['title'] == 'Insert Test'
        assert song['artist'] == 'Test Artist'

    def test_insert_rating(self, test_app):
        """Test inserting a rating into the database."""
        conn = get_db_connection()

        # Create song
        conn.execute(
            "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
            ('Rating Insert Test', 'Artist', 'Album', '2025')
        )
        conn.commit()

        song = conn.execute(
            "SELECT id FROM songs WHERE title = ?",
            ('Rating Insert Test',)
        ).fetchone()
        song_id = song[0]

        # Insert rating
        conn.execute(
            "INSERT INTO ratings (song_id, user_id, rating) VALUES (?, ?, ?)",
            (song_id, 'test_user_123', 1)
        )
        conn.commit()

        rating = conn.execute(
            "SELECT * FROM ratings WHERE song_id = ? AND user_id = ?",
            (song_id, 'test_user_123')
        ).fetchone()

        conn.close()

        assert rating is not None
        assert rating['rating'] == 1
        assert rating['user_id'] == 'test_user_123'

    def test_update_rating(self, test_app):
        """Test updating an existing rating."""
        conn = get_db_connection()

        # Create song
        conn.execute(
            "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
            ('Update Rating Test', 'Artist', 'Album', '2025')
        )
        conn.commit()

        song = conn.execute(
            "SELECT id FROM songs WHERE title = ?",
            ('Update Rating Test',)
        ).fetchone()
        song_id = song[0]

        # Insert initial rating
        conn.execute(
            "INSERT INTO ratings (song_id, user_id, rating) VALUES (?, ?, ?)",
            (song_id, 'update_user', 1)
        )
        conn.commit()

        # Update rating
        conn.execute(
            "UPDATE ratings SET rating = ? WHERE song_id = ? AND user_id = ?",
            (-1, song_id, 'update_user')
        )
        conn.commit()

        updated_rating = conn.execute(
            "SELECT rating FROM ratings WHERE song_id = ? AND user_id = ?",
            (song_id, 'update_user')
        ).fetchone()

        conn.close()

        assert updated_rating['rating'] == -1

    def test_aggregate_ratings(self, test_app):
        """Test counting thumbs up and thumbs down for a song."""
        conn = get_db_connection()

        # Create song
        conn.execute(
            "INSERT INTO songs (title, artist, album, year) VALUES (?, ?, ?, ?)",
            ('Aggregate Test', 'Artist', 'Album', '2025')
        )
        conn.commit()

        song = conn.execute(
            "SELECT id FROM songs WHERE title = ?",
            ('Aggregate Test',)
        ).fetchone()
        song_id = song[0]

        # Insert multiple ratings
        ratings_data = [
            (song_id, 'user1', 1),
            (song_id, 'user2', 1),
            (song_id, 'user3', -1),
            (song_id, 'user4', 1),
        ]

        for rating_data in ratings_data:
            conn.execute(
                "INSERT INTO ratings (song_id, user_id, rating) VALUES (?, ?, ?)",
                rating_data
            )
        conn.commit()

        # Aggregate counts
        counts = conn.execute('''
            SELECT
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as thumbs_up,
                SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as thumbs_down
            FROM ratings
            WHERE song_id = ?
        ''', (song_id,)).fetchone()

        conn.close()

        assert counts['thumbs_up'] == 3
        assert counts['thumbs_down'] == 1
