from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

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
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/radio')
def radio():
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

if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists(DATABASE):
        init_db()
        print(f'Database {DATABASE} created successfully!')

    print('Starting Flask server...')
    print('Visit http://127.0.0.1:5000 in your browser')
    app.run(debug=True, host='127.0.0.1', port=5000)
