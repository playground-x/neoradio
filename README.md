# NeoRadio

A modern web-based radio player for streaming HLS audio with live metadata display, track history, and community song ratings.

![NeoRadio](https://img.shields.io/badge/status-active-success.svg)
![Flask](https://img.shields.io/badge/flask-3.1.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)

## Overview

NeoRadio is a Flask-based web application that provides a sleek, dark-themed interface for listening to live radio streams. Features include real-time track metadata, album artwork, an animated visualizer, and a community-driven rating system for songs.

## Features

- **HLS Audio Streaming** - Lossless quality streaming with auto-recovery from errors
- **Live Metadata** - Real-time track information (title, artist, album, year)
- **Album Artwork** - Auto-refreshing cover images for each track
- **Track History** - Last 10 played tracks with timestamps
- **Song Ratings** - Community thumbs up/down voting system
- **Animated Visualizer** - 40-bar audio visualization
- **Dark Theme** - Modern purple/blue gradient design
- **Responsive Layout** - Mobile-friendly grid design
- **IP-Based User Identification** - Persistent ratings without cookies

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/playground-x/neoradio.git
cd neoradio
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
Access at: http://localhost:5000/radio

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```
Access at: http://localhost/radio

### 3. Install Dependencies

### Local Development

### 4. Run the Application

2. **Run the application:**
   ```bash
   python app.py
   ```

The server will start at: **http://127.0.0.1:5000**

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

- Flask web framework
- SQLite database (no separate database server needed)
- RESTful API endpoints
- Automatic database initialisation
- Interactive web UI for testing

## Development

### Debug Mode
The server runs in debug mode by default:
- Auto-reloads on code changes
- Detailed error messages
- Interactive debugger

### Metadata Polling
JavaScript polls for metadata every 10 seconds to keep track info current.

### Database Auto-Initialization
The database is automatically created on first run with all required tables.

## Color Scheme

- **Background Gradient:** `#2d2b6b` → `#49264e`
- **Cards:** `#1a1a1a`
- **Sections:** `#252525`
- **Accent:** `#7b8ff7` (purple/blue)
- **Buttons:** `#5568d3` (blue), `#c62828` (red)
- **Success:** `#4caf50` (green)
- **Error:** `#ff5252` (red)

## Browser Support

- **Chrome/Edge:** Requires HLS.js
- **Firefox:** Requires HLS.js
- **Safari:** Native HLS support
- **Mobile:** Full responsive design

## Documentation

For detailed technical documentation, see [CLAUDE.md](CLAUDE.md) which includes:
- Complete architecture overview
- API endpoint specifications
- Database schema details
- Security considerations
- Troubleshooting guide
- Future enhancement ideas

## License

[Specify your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

[Your contact information]

## Acknowledgments

Built with [Claude Code](https://claude.com/claude-code)
