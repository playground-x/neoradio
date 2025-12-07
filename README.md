# NeoRadio - Local Development Environment

A Flask-based web server with SQLite database for local prototyping.

## Setup

### 1. Activate Virtual Environment

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python app.py
```

The server will start at: http://127.0.0.1:5000

### 4. Run Security Scans (Optional)

```bash
# Run npm audit for Node.js dependencies
npm run security

# Run all security scans (npm + Python)
npm run security:all

# Run Python security scan only
python security_scan.py
```

See [SECURITY.md](SECURITY.md) for detailed security scanning documentation.

## Project Structure

```
neoradio/
├── venv/                # Virtual environment (not committed)
├── app.py               # Flask application with API routes
├── database.db          # SQLite database (created on first run)
├── templates/           # HTML templates
│   └── index.html       # Main page with demo UI
├── static/              # Static files (CSS, JS, images)
├── requirements.txt     # Python dependencies
├── package.json         # npm configuration & security scripts
├── package-lock.json    # npm dependency lock file
├── security_scan.py     # Python security scanner
├── security.ps1         # PowerShell security script (Windows)
├── Makefile             # Make targets for security & development
├── SECURITY.md          # Security scanning documentation
└── README.md            # This file
```

## API Endpoints

### Users

- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com"
  }
  ```

### Posts

- `GET /api/posts` - Get all posts
- `POST /api/posts` - Create a new post
  ```json
  {
    "user_id": 1,
    "title": "My First Post",
    "content": "Hello world!"
  }
  ```

## Database Schema

### Users Table
- `id` - Primary key
- `name` - User's name
- `email` - User's email (unique)
- `created_at` - Timestamp

### Posts Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `title` - Post title
- `content` - Post content
- `created_at` - Timestamp

## Features

- Flask web framework
- SQLite database (no separate database server needed)
- RESTful API endpoints
- Automatic database initialization
- Debug mode enabled for development
- Interactive web UI for testing

## Development

The server runs in debug mode, which means:
- Auto-reloads when you change code
- Detailed error messages
- Interactive debugger in the browser

To modify the database schema, edit the `init_db()` function in `app.py`.

## Next Steps

- Add more API endpoints as needed
- Create additional database tables
- Build out your frontend in `templates/`
- Add authentication if needed
- Customize for your specific use case
