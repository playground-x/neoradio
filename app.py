from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
# Secret key for sessions - needed to track user ratings
app.secret_key = os.environ.get('SECRET_KEY', 'neoradio-secret-key-change-in-production')

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE = os.environ.get('DATABASE', 'database.db')
USE_POSTGRES = DATABASE_URL is not None

# Import psycopg2 only if using PostgreSQL
if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras

def get_db_connection():
    """Create a database connection (SQLite or PostgreSQL)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(conn, query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query with cursor, compatible with both SQLite and PostgreSQL.

    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters (tuple)
        fetch_one: Return single row as dict
        fetch_all: Return all rows as list of dicts

    Returns:
        Dictionary or list of dictionaries for SELECT queries, None for INSERT/UPDATE
    """
    cursor = conn.cursor() if not USE_POSTGRES else conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Convert SQLite placeholders (?) to PostgreSQL placeholders (%s)
    if USE_POSTGRES and query:
        query = query.replace('?', '%s')
        # Handle INSERT OR IGNORE for PostgreSQL - convert to ON CONFLICT DO NOTHING
        if 'INSERT OR IGNORE' in query:
            # Extract table name and columns
            import re
            match = re.search(r'INSERT OR IGNORE INTO (\w+)\s*\(([^)]+)\)', query)
            if match:
                table = match.group(1)
                # For songs table, conflict is on (title, artist)
                if table == 'songs':
                    query = query.replace('INSERT OR IGNORE', 'INSERT') + ' ON CONFLICT (title, artist) DO NOTHING'
                else:
                    query = query.replace('INSERT OR IGNORE', 'INSERT')

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    if fetch_one:
        result = cursor.fetchone()
        cursor.close()
        return dict(result) if result and USE_POSTGRES else dict(result) if result else None
    elif fetch_all:
        results = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in results] if USE_POSTGRES else [dict(row) for row in results]
    else:
        cursor.close()
        return None

def init_db():
    """Initialize the database with tables (supports both SQLite and PostgreSQL)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                album TEXT,
                year TEXT,
                UNIQUE(title, artist)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id SERIAL PRIMARY KEY,
                song_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating IN (1, -1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(song_id, user_id),
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        ''')
    else:
        # SQLite syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                album TEXT,
                year TEXT,
                UNIQUE(title, artist)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating IN (1, -1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(song_id, user_id),
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        ''')

    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
@app.route('/radio')
def index():
    """Radio player page"""
    return render_template('radio.html')

@app.route('/api/metadata')
def get_metadata():
    """Fetch current track metadata from stream"""
    import requests
    try:
        # Fetch metadata from metadatav2.json at the stream host
        metadata_url = 'https://d3d4yli4hf5bmh.cloudfront.net/metadatav2.json'
        response = requests.get(metadata_url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'source': metadata_url,
                'data': data
            })
        else:
            return jsonify({'error': f'HTTP {response.status_code}'}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/rating', methods=['POST'])
def rate_song():
    """Rate a song (thumbs up = 1, thumbs down = -1)"""
    import hashlib

    conn = get_db_connection()
    data = request.get_json()

    # Get user's IP address
    if request.headers.get('X-Forwarded-For'):
        # If behind proxy, get real IP
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip_address = request.remote_addr

    # Get User-Agent for additional fingerprinting
    user_agent = request.headers.get('User-Agent', '')

    # Create a persistent user identifier based on IP + User-Agent hash
    # This prevents cookie clearing but still maintains some privacy
    identifier_string = f"{ip_address}:{user_agent}"
    user_id = hashlib.sha256(identifier_string.encode()).hexdigest()[:32]
    title = data.get('title')
    artist = data.get('artist')
    album = data.get('album', '')
    year = data.get('year', '')
    rating = data.get('rating')  # 1 for thumbs up, -1 for thumbs down

    if not title or not artist or rating not in [1, -1]:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        # Insert or get song
        execute_query(conn, '''
            INSERT OR IGNORE INTO songs (title, artist, album, year)
            VALUES (?, ?, ?, ?)
        ''', (title, artist, album, year))
        conn.commit()

        song = execute_query(conn, '''
            SELECT id FROM songs WHERE title = ? AND artist = ?
        ''', (title, artist), fetch_one=True)

        song_id = song['id']

        # Try to insert rating, if user already rated, update it
        IntegrityError = psycopg2.IntegrityError if USE_POSTGRES else sqlite3.IntegrityError
        try:
            execute_query(conn, '''
                INSERT INTO ratings (song_id, user_id, rating)
                VALUES (?, ?, ?)
            ''', (song_id, user_id, rating))
            conn.commit()
        except IntegrityError:
            # User already rated, update the rating
            # For PostgreSQL, we need to rollback the failed transaction first
            conn.rollback()
            execute_query(conn, '''
                UPDATE ratings SET rating = ?
                WHERE song_id = ? AND user_id = ?
            ''', (rating, song_id, user_id))
            conn.commit()

        # Get updated counts
        counts = execute_query(conn, '''
            SELECT
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as thumbs_up,
                SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as thumbs_down
            FROM ratings
            WHERE song_id = ?
        ''', (song_id,), fetch_one=True)

        conn.close()

        return jsonify({
            'success': True,
            'thumbs_up': counts['thumbs_up'] or 0,
            'thumbs_down': counts['thumbs_down'] or 0
        })

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/rating/<title>/<artist>')
def get_song_rating(title, artist):
    """Get rating counts for a specific song"""
    conn = get_db_connection()

    song = execute_query(conn, '''
        SELECT id FROM songs WHERE title = ? AND artist = ?
    ''', (title, artist), fetch_one=True)

    if not song:
        conn.close()
        return jsonify({'thumbs_up': 0, 'thumbs_down': 0, 'user_rating': None})

    song_id = song['id']

    # Get counts
    counts = execute_query(conn, '''
        SELECT
            SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as thumbs_up,
            SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as thumbs_down
        FROM ratings
        WHERE song_id = ?
    ''', (song_id,), fetch_one=True)

    # Get user's rating if they have one
    import hashlib

    # Get user's IP address
    if request.headers.get('X-Forwarded-For'):
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip_address = request.remote_addr

    # Get User-Agent for additional fingerprinting
    user_agent = request.headers.get('User-Agent', '')

    # Create a persistent user identifier based on IP + User-Agent hash
    identifier_string = f"{ip_address}:{user_agent}"
    user_id = hashlib.sha256(identifier_string.encode()).hexdigest()[:32]

    user_rating = None
    user_rating_row = execute_query(conn, '''
        SELECT rating FROM ratings WHERE song_id = ? AND user_id = ?
    ''', (song_id, user_id), fetch_one=True)
    if user_rating_row:
        user_rating = user_rating_row['rating']

    conn.close()

    return jsonify({
        'thumbs_up': counts['thumbs_up'] or 0,
        'thumbs_down': counts['thumbs_down'] or 0,
        'user_rating': user_rating
    })

# Database initialization flag
_db_initialized = False

@app.before_request
def initialize_database():
    """Initialize database before first request"""
    global _db_initialized
    if not _db_initialized:
        if USE_POSTGRES:
            # For PostgreSQL, always try to initialize (init-db.sql handles IF NOT EXISTS)
            try:
                init_db()
                print('PostgreSQL database initialized!')
            except Exception as e:
                print(f'Database initialization note: {e}')
        else:
            # For SQLite, check if tables exist
            try:
                conn = get_db_connection()
                result = execute_query(conn, "SELECT name FROM sqlite_master WHERE type='table' AND name='songs'", fetch_one=True)
                conn.close()
                if not result:
                    # Tables don't exist, initialize
                    init_db()
                    print(f'SQLite database {DATABASE} initialized!')
            except Exception as e:
                print(f'Database check/initialization error: {e}')
        _db_initialized = True

if __name__ == '__main__':
    print('Starting Flask server...')
    print('Visit http://127.0.0.1:5000 in your browser')
    app.run(debug=True, host='127.0.0.1', port=5000)
