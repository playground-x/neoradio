# NeoRadio

A modern web-based radio player for streaming HLS (HTTP Live Streaming) audio with live metadata display, track history, and community song ratings.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- **HLS Audio Streaming** - Live radio playback with CloudFront CDN
- **Live Metadata** - Real-time track information updates every 10 seconds
- **Album Artwork** - Dynamic cover art display with cache-busting
- **Animated Visualizer** - 40-bar audio visualizer animation
- **Track History** - Last 10 played tracks with timestamps
- **Community Ratings** - Thumbs up/down voting system for songs
- **IP-Based User ID** - Persistent user identification without cookies
- **Dark Theme** - Purple/blue gradient with modern UI
- **Responsive Design** - Mobile-friendly layout

## Quick Start

### Docker (Recommended)

**Development with SQLite:**
```bash
docker-compose up dev
```
Access at: http://localhost:5000/radio

**Production with PostgreSQL + Nginx:**
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY and POSTGRES_PASSWORD

# 2. Start all production services
docker-compose up -d postgres app nginx
```
Access at: http://localhost/radio

See [DOCKER.md](DOCKER.md) for complete deployment guide including database migration and configuration options.

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access the player:**
   - Open browser to `http://127.0.0.1:5000/radio`

## Project Structure

```
neoradio/
├── app.py                      # Flask application with routes and API
├── requirements.txt            # Python dependencies
├── database.db                 # SQLite database (auto-created)
├── templates/
│   └── radio.html             # Radio player interface
├── static/
│   ├── css/
│   │   └── radio.css          # Player styling
│   └── js/
│       └── radio.js           # Player functionality
├── tests/                      # Test suite (pytest)
│   ├── conftest.py            # Test fixtures
│   ├── test_database.py       # Database tests
│   ├── test_routes.py         # API endpoint tests
│   └── test_user_identification.py  # User ID tests
├── Dockerfile                  # Production Docker image
├── Dockerfile.dev              # Development Docker image
├── docker-compose.yml          # Docker orchestration (dev + prod stacks)
├── .dockerignore              # Docker build exclusions
├── .env.example               # Environment variable template
├── init-db.sql                # PostgreSQL initialization script
├── nginx.conf                 # Nginx reverse proxy configuration
├── pytest.ini                 # Test configuration
├── DOCKER.md                  # Docker deployment guide
├── CLAUDE.md                  # Technical documentation
└── README.md                  # This file
```

## Technology Stack

- **Backend:** Flask 3.1.2, SQLite/PostgreSQL (dual database support)
- **Frontend:** Vanilla JavaScript, HLS.js, CSS Grid
- **Deployment:** Docker, Docker Compose, Nginx, Gunicorn
- **Testing:** pytest (29 tests, 73% coverage)
```

## API Endpoints

### `GET /radio`
Radio player interface

### `GET /api/metadata`
Fetches current track metadata from stream server

**Response:**
```json
{
  "source": "api",
  "data": {
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "date": "2024"
  }
}
```

### `POST /api/songs/rating`
Submit or update a song rating

**Request:**
```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "year": "2024",
  "rating": 1
}
```
- `rating`: 1 for thumbs up, -1 for thumbs down

**Response:**
```json
{
  "success": true,
  "thumbs_up": 42,
  "thumbs_down": 5
}
```

### `GET /api/songs/rating/<title>/<artist>`
Get rating counts and user's rating for a song

**Response:**
```json
{
  "thumbs_up": 42,
  "thumbs_down": 5,
  "user_rating": 1
}
```

## Database Schema

NeoRadio supports both SQLite (development) and PostgreSQL (production) with identical schema.

### songs
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/AUTOINCREMENT | Primary key |
| title | TEXT | Song title |
| artist | TEXT | Artist name |
| album | TEXT | Album name (optional) |
| year | TEXT | Release year (optional) |

**Constraints:** UNIQUE(title, artist)

### ratings
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL/AUTOINCREMENT | Primary key |
| song_id | INTEGER | Foreign key to songs.id |
| user_id | TEXT | SHA256 hash of IP + User-Agent |
| rating | INTEGER | 1 (thumbs up) or -1 (thumbs down) |
| created_at | TIMESTAMP | Rating timestamp |

**Constraints:**
- UNIQUE(song_id, user_id) - Prevents duplicate ratings
- CHECK(rating IN (1, -1)) - Enforces valid rating values
- Foreign key cascade on delete

**PostgreSQL Performance Indexes:**
- `idx_ratings_song_id` on `ratings.song_id`
- `idx_ratings_user_id` on `ratings.user_id`
- `idx_songs_artist` on `songs.artist`
- `idx_songs_title` on `songs.title`

## User Identification

NeoRadio uses IP-based fingerprinting to prevent rating manipulation:

1. Extracts client IP (handles `X-Forwarded-For` for proxies)
2. Combines with User-Agent string
3. Creates SHA256 hash: `hashlib.sha256(f"{ip}:{user_agent}".encode())`
4. Uses first 32 characters as `user_id`

This approach:
- Prevents cookie clearing exploits
- Maintains user privacy through hashing
- Persists across browser sessions
- Requires IP/browser change to bypass

## Technology Stack

**Backend:**
- Flask 3.1.2 - Python web framework
- SQLite - Embedded database
- Requests 2.32.5 - HTTP library
- Gunicorn 21.2.0 - WSGI HTTP server (production)

**Frontend:**
- HLS.js - JavaScript HLS stream playback
- Vanilla JavaScript - No framework dependencies
- CSS Grid - Responsive layout

**Testing:**
- pytest 8.3.4 - Testing framework
- pytest-cov 6.0.0 - Coverage reporting

**Deployment:**
- Docker - Containerization
- Docker Compose - Multi-container orchestration

## Color Scheme

- **Background:** Gradient `#2d2b6b` → `#49264e`
- **Cards:** Dark `#1a1a1a` with `#252525` sections
- **Accents:** Purple/blue `#7b8ff7`
- **Buttons:** Blue `#5568d3`, Red `#c62828`
- **Success:** Green `#4caf50`
- **Error:** Red `#ff5252`

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest -v

# Run with coverage
python -m pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Test Coverage:** 73% on app.py (29 tests passing)

## Configuration

### Environment Variables

- `SECRET_KEY` - Flask secret key (required for production)
- `DATABASE` - Database file path (default: `database.db`)

### Stream Configuration

Edit [app.py](app.py) to change stream URLs:
- **Stream URL:** `https://d3d4yli4hf5bmh.cloudfront.net/hls/live.m3u8`
- **Metadata URL:** `https://d3d4yli4hf5bmh.cloudfront.net/metadata`
- **Album Art URL:** `https://d3d4yli4hf5bmh.cloudfront.net/cover.jpg`

## Browser Support

- **Chrome/Edge:** HLS.js required ✅
- **Firefox:** HLS.js required ✅
- **Safari:** Native HLS support ✅
- **Mobile:** Responsive design ✅

## Deployment

### Docker (Production)

See [DOCKER.md](DOCKER.md) for complete deployment guide.

Quick start:
```bash
# Set secret key
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Run production container
docker-compose up -d prod
```

### Traditional Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY=your-secret-key
export FLASK_ENV=production

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## Development

The application runs in debug mode when executed directly:
- Auto-reloads on code changes
- Detailed error messages
- Interactive debugger

Hot reload is enabled in Docker dev mode via volume mounting.

## Documentation

- [DOCKER.md](DOCKER.md) - Docker deployment guide
- [CLAUDE.md](CLAUDE.md) - Detailed technical documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
