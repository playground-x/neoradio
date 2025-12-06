from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
# Secret key for sessions - needed to track user ratings
app.secret_key = 'neoradio-secret-key-change-in-production'

# Database configuration
DATABASE = 'database.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with sample tables"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            year TEXT,
            UNIQUE(title, artist)
        )
    ''')
    conn.execute('''
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
    conn.close()

@app.route('/')
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

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """Get all users or create a new user"""
    conn = get_db_connection()

    if request.method == 'POST':
        data = request.get_json()
        conn.execute('INSERT INTO users (name, email) VALUES (?, ?)',
                    (data['name'], data['email']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User created successfully'}), 201

    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    """Get all posts or create a new post"""
    conn = get_db_connection()

    if request.method == 'POST':
        data = request.get_json()
        conn.execute('INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)',
                    (data['user_id'], data['title'], data['content']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Post created successfully'}), 201

    posts = conn.execute('''
        SELECT posts.*, users.name as author_name
        FROM posts
        LEFT JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(post) for post in posts])

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
        conn.execute('''
            INSERT OR IGNORE INTO songs (title, artist, album, year)
            VALUES (?, ?, ?, ?)
        ''', (title, artist, album, year))
        conn.commit()

        song = conn.execute('''
            SELECT id FROM songs WHERE title = ? AND artist = ?
        ''', (title, artist)).fetchone()

        song_id = song['id']

        # Try to insert rating, if user already rated, update it
        try:
            conn.execute('''
                INSERT INTO ratings (song_id, user_id, rating)
                VALUES (?, ?, ?)
            ''', (song_id, user_id, rating))
            conn.commit()
        except sqlite3.IntegrityError:
            # User already rated, update the rating
            conn.execute('''
                UPDATE ratings SET rating = ?
                WHERE song_id = ? AND user_id = ?
            ''', (rating, song_id, user_id))
            conn.commit()

        # Get updated counts
        counts = conn.execute('''
            SELECT
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as thumbs_up,
                SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as thumbs_down
            FROM ratings
            WHERE song_id = ?
        ''', (song_id,)).fetchone()

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

    song = conn.execute('''
        SELECT id FROM songs WHERE title = ? AND artist = ?
    ''', (title, artist)).fetchone()

    if not song:
        conn.close()
        return jsonify({'thumbs_up': 0, 'thumbs_down': 0, 'user_rating': None})

    song_id = song['id']

    # Get counts
    counts = conn.execute('''
        SELECT
            SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as thumbs_up,
            SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as thumbs_down
        FROM ratings
        WHERE song_id = ?
    ''', (song_id,)).fetchone()

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
    user_rating_row = conn.execute('''
        SELECT rating FROM ratings WHERE song_id = ? AND user_id = ?
    ''', (song_id, user_id)).fetchone()
    if user_rating_row:
        user_rating = user_rating_row['rating']

    conn.close()

    return jsonify({
        'thumbs_up': counts['thumbs_up'] or 0,
        'thumbs_down': counts['thumbs_down'] or 0,
        'user_rating': user_rating
    })

if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists(DATABASE):
        init_db()
        print(f'Database {DATABASE} created successfully!')

    print('Starting Flask server...')
    print('Visit http://127.0.0.1:5000 in your browser')
    app.run(debug=True, host='127.0.0.1', port=5000)
