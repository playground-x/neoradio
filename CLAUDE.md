# NeoRadio

A modern web-based radio player for streaming HLS (HTTP Live Streaming) audio with live metadata display, track history, and community song ratings.

## Project Overview

NeoRadio is a Flask-based web application that provides a sleek, dark-themed interface for listening to live radio streams. It features real-time track metadata, album artwork, an animated visualizer, and a community-driven rating system for songs.

## Technology Stack

### Backend
- **Flask 3.1.2** - Python web framework
- **SQLite** - Database for storing songs and ratings
- **Requests 2.32.5** - HTTP library for fetching stream metadata
- **Gunicorn 21.2.0** - WSGI HTTP server for production

### Frontend
- **HLS.js** - JavaScript library for HLS stream playback
- **Vanilla JavaScript** - No framework dependencies
- **CSS Grid** - Responsive layout system

### Testing
- **pytest 8.3.4** - Testing framework
- **pytest-cov 6.0.0** - Code coverage reporting

### Deployment
- **Docker** - Containerization platform
- **Docker Compose** - Multi-container orchestration

## Architecture

### File Structure

```
neoradio/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies (Flask, Requests, Gunicorn, pytest)
├── database.db                 # SQLite database (auto-created)
├── templates/
│   └── radio.html             # Radio player page
├── static/
│   ├── css/
│   │   └── radio.css          # Player styling
│   └── js/
│       └── radio.js           # Player functionality
├── tests/                      # Test suite
│   ├── conftest.py            # pytest fixtures
│   ├── test_database.py       # Database tests
│   ├── test_routes.py         # API route tests
│   └── test_user_identification.py  # User ID tests
├── Dockerfile                  # Production Docker image
├── Dockerfile.dev              # Development Docker image
├── docker-compose.yml          # Docker orchestration
├── .dockerignore              # Docker build exclusions
├── .env.example               # Environment variable template
├── pytest.ini                 # pytest configuration
├── DOCKER.md                  # Docker deployment guide
├── CLAUDE.md                  # Technical documentation (this file)
└── README.md                  # User-facing documentation
```

### Database Schema

**songs** table:
- `id` (INTEGER PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `artist` (TEXT NOT NULL)
- `album` (TEXT)
- `year` (TEXT)
- UNIQUE constraint on (title, artist)

**ratings** table:
- `id` (INTEGER PRIMARY KEY)
- `song_id` (INTEGER, FK to songs.id)
- `user_id` (TEXT) - SHA256 hash of IP + User-Agent
- `rating` (INTEGER) - 1 for thumbs up, -1 for thumbs down
- `created_at` (TIMESTAMP)
- UNIQUE constraint on (song_id, user_id)

## Key Features

### 1. HLS Audio Streaming
- Streams from CloudFront CDN: `https://d3d4yli4hf5bmh.cloudfront.net/hls/live.m3u8`
- Supports both HLS.js (Chrome, Firefox) and native HLS (Safari)
- Auto-recovery from network and media errors
- Volume control with visual feedback

### 2. Live Metadata
- Fetches track information from API every 10 seconds
- Displays: track title, artist, album, year
- Updates album artwork with cache-busting
- Parses both ID3 tags and API metadata

### 3. Visual Features
- **Animated Visualizer**: 40 bars with randomized heights
- **Album Art**: Auto-refreshing cover images
- **Track History**: Last 10 played tracks with timestamps
- **Dark Theme**: Purple/blue gradient with #1a1a1a cards

### 4. Song Rating System
- Thumbs up/down voting for each track
- IP + User-Agent fingerprinting for user identification
- Prevents duplicate ratings from same user
- Real-time rating count display
- Visual feedback for user's active rating

### 5. Responsive Design
- Grid layout: 2fr (player) + 1fr (history) on desktop
- Stacks vertically on screens < 1024px
- Mobile-friendly controls and typography

## API Endpoints

### GET `/` or GET `/radio`
Radio player interface

### GET `/api/metadata`
Fetches current track metadata from stream server
- Returns: `{source, data: {title, artist, album, date}}`

### POST `/api/songs/rating`
Submit or update a song rating
- Body: `{title, artist, album, year, rating}`
- Rating: 1 (thumbs up) or -1 (thumbs down)
- Returns: `{success, thumbs_up, thumbs_down}`

### GET `/api/songs/rating/<title>/<artist>`
Get rating counts and user's rating for a song
- Returns: `{thumbs_up, thumbs_down, user_rating}`

## User Identification

Uses IP-based fingerprinting to prevent rating manipulation:
1. Extracts client IP (handles X-Forwarded-For for proxies)
2. Combines with User-Agent string
3. Creates SHA256 hash: `hashlib.sha256(f"{ip}:{user_agent}".encode())`
4. Uses first 32 characters as user_id

This approach:
- Prevents cookie clearing exploits
- Maintains user privacy through hashing
- Persists across browser sessions
- Requires IP/browser change to bypass

## Docker Architecture

NeoRadio supports containerized deployment with separate configurations for development and production.

### Docker Images

#### Production (`Dockerfile`)
- **Base:** `python:3.11-slim` (Debian Trixie)
- **Server:** Gunicorn with 4 workers
- **User:** Non-root `neoradio:1000` for security
- **Health Checks:** Automated container monitoring
- **Port:** 5000 (internal)
- **Size:** ~451MB

#### Development (`Dockerfile.dev`)
- **Base:** `python:3.11-slim` (Debian Trixie)
- **Server:** Flask development server with debug mode
- **Hot Reload:** Code changes reflect immediately via volume mounts
- **Port:** 5000 (internal)
- **Size:** ~450MB

### Docker Compose Services

#### `dev` Service
- **Port Mapping:** `5000:5000`
- **Volumes:**
  - Source code mounted for hot reload
  - Persistent database volume: `neoradio-dev-data`
- **Environment:** `FLASK_ENV=development`, `FLASK_DEBUG=1`
- **Restart Policy:** `unless-stopped`

#### `prod` Service
- **Port Mapping:** `8080:5000`
- **Volumes:**
  - Database only: `neoradio-prod-data`
  - Source code baked into image
- **Environment:** `FLASK_ENV=production`, `SECRET_KEY` from env
- **Restart Policy:** `always`
- **Health Checks:** Every 30s with 3 retries

### Environment Variables

- `SECRET_KEY` - Flask secret key (required for production)
- `DATABASE` - Database file path (default: `/app/data/database.db`)
- `FLASK_ENV` - Flask environment (`development` or `production`)
- `FLASK_DEBUG` - Debug mode flag (`0` or `1`)

### Volume Persistence

- **Development:** `neoradio-dev-data` - Development database and uploaded files
- **Production:** `neoradio-prod-data` - Production database and uploaded files

Both volumes are Docker-managed and persist data across container restarts.

### Security Features

- Non-root user execution in production
- Secret key management via environment variables
- Database isolation in Docker volumes
- Health check monitoring
- Resource limits configurable via docker-compose

### Deployment Workflows

**Quick Development:**
```bash
docker-compose up dev
```

**Production Deployment:**
```bash
# Generate secret key
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
echo "SECRET_KEY=$SECRET_KEY" > .env

# Start production service
docker-compose up -d prod

# View logs
docker-compose logs -f prod

# Check health
docker inspect --format='{{.State.Health.Status}}' neoradio-prod
```

For complete Docker documentation, see [DOCKER.md](DOCKER.md).

## Testing

### Test Suite

NeoRadio includes a comprehensive test suite with 29 tests achieving 73% code coverage.

**Test Files:**
- `tests/test_database.py` - Database schema, constraints, CRUD operations (11 tests)
- `tests/test_routes.py` - API endpoints, UI elements (11 tests)
- `tests/test_user_identification.py` - IP-based fingerprinting (7 tests)

**Running Tests:**
```bash
# Local
python -m pytest -v

# With coverage
python -m pytest --cov=app --cov-report=html

# In Docker
docker-compose exec dev pytest -v
```

**Test Features:**
- Isolated test database via fixtures
- Windows-specific database locking handled
- Coverage reporting (HTML and terminal)
- Parallel test execution support

## Color Scheme

### Background
- Body gradient: `#2d2b6b` → `#49264e`
- Player/history cards: `#1a1a1a`
- Nested sections: `#252525`

### Accents
- Primary purple/blue: `#7b8ff7`
- Buttons: `#5568d3` (blue), `#c62828` (red stop)
- Success: `#4caf50` (green thumbs up)
- Error: `#ff5252` (red thumbs down)

### Text
- Primary: `#fff` (white)
- Secondary: `#7b8ff7` (purple/blue)
- Tertiary: `#aaa`, `#bbb`, `#ccc` (grays)

## Setup Instructions

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the player**:
   - Open browser to `http://127.0.0.1:5000/radio`

4. **Database initialization**:
   - Database is auto-created on first run
   - No manual setup required

### Docker Deployment

#### Development with Docker

```bash
# Build and run development container
docker-compose up dev

# Access at http://localhost:5000/radio
# Hot reload enabled - changes to code reflect immediately
```

#### Production with Docker

```bash
# Build and run production container
docker-compose up prod

# Access at http://localhost:8080/radio
# Runs with gunicorn and 4 workers
```

#### Docker Configuration

**Environment Variables** (create `.env` file):
```bash
SECRET_KEY=your-secret-key-here
DATABASE=/app/data/database.db
```

**Build individual containers**:
```bash
# Development
docker build -f Dockerfile.dev -t neoradio:dev .

# Production
docker build -f Dockerfile -t neoradio:prod .
```

**Run standalone containers**:
```bash
# Development
docker run -p 5000:5000 -v $(pwd):/app neoradio:dev

# Production
docker run -p 8080:5000 \
  -e SECRET_KEY=your-secret-key \
  -v neoradio-data:/app/data \
  neoradio:prod
```

**Docker Features**:
- Non-root user for security
- Volume persistence for database
- Health checks for production
- Hot reload for development
- Optimized layer caching

## Development Notes

### Metadata Polling
- JavaScript polls `/api/metadata` every 10 seconds
- Updates track info only when title or artist changes
- Prevents duplicate entries in track history

### Album Art Caching
- Uses cache-busting query parameter: `?t=${Date.now()}`
- Ensures fresh album art on track changes
- URL: `https://d3d4yli4hf5bmh.cloudfront.net/cover.jpg`

### Error Handling
- HLS errors trigger auto-recovery (network/media)
- Rating submission fails gracefully with console errors
- Metadata fetch failures are silent (expected when API unavailable)

### Security Considerations
- Secret key hardcoded (change in production!)
- SQL injection prevented via parameterized queries
- XSS prevented via textContent (not innerHTML)
- No CSRF protection (consider adding for production)

## Browser Compatibility

- **Chrome/Edge**: HLS.js required
- **Firefox**: HLS.js required
- **Safari**: Native HLS support
- **Mobile**: Responsive design, native controls

## Future Enhancements

Potential improvements:
- User accounts and authentication
- Playlist creation and management
- Social features (comments, sharing)
- Advanced analytics (most rated songs, trending)
- Admin panel for content moderation
- WebSocket for real-time metadata updates
- Audio quality selection
- Download track history as CSV/JSON

## Troubleshooting

### Stream won't play
- Check browser console for HLS errors
- Verify stream URL is accessible
- Ensure HLS.js is loaded correctly

### Metadata not updating
- Check `/api/metadata` endpoint response
- Verify metadata URL is accessible
- Check browser console for fetch errors

### Ratings not working
- Verify database.db exists and is writable
- Check POST request in network tab
- Ensure user_id generation is working

## License

[Specify your license here]

## Contact

[Your contact information]
