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

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The server will start at: **http://127.0.0.1:5000**

## Project Structure

```
neoradio/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── database.db                 # SQLite database (auto-created)
├── CLAUDE.md                   # Detailed project documentation
├── README.md                   # This file
├── templates/
│   └── radio.html             # Radio player interface
└── static/
    ├── css/
    │   └── radio.css          # Player styling
    └── js/
        └── radio.js           # Player functionality
```

## API Endpoints

### Metadata
- `GET /api/metadata` - Fetch current track metadata from stream

### Song Ratings
- `POST /api/songs/rating` - Submit or update a song rating
  ```json
  {
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "year": "2025",
    "rating": 1  // 1 for thumbs up, -1 for thumbs down
  }
  ```

- `GET /api/songs/rating/<title>/<artist>` - Get rating counts and user's rating
  ```json
  {
    "thumbs_up": 42,
    "thumbs_down": 7,
    "user_rating": 1  // null if user hasn't rated
  }
  ```

## Database Schema

### Songs Table
- `id` - Primary key
- `title` - Song title
- `artist` - Artist name
- `album` - Album name
- `year` - Release year
- UNIQUE constraint on (title, artist)

### Ratings Table
- `id` - Primary key
- `song_id` - Foreign key to songs
- `user_id` - SHA256 hash of IP + User-Agent
- `rating` - 1 (thumbs up) or -1 (thumbs down)
- `created_at` - Timestamp
- UNIQUE constraint on (song_id, user_id)

## Technology Stack

- **Backend:** Flask 3.1.2
- **Database:** SQLite
- **Frontend:** Vanilla JavaScript, CSS Grid
- **Streaming:** HLS.js for audio playback
- **HTTP Client:** Requests 2.32.5

## Configuration

### Stream URL
The stream URL is configured in `static/js/radio.js`:
```javascript
const streamUrl = 'https://d3d4yli4hf5bmh.cloudfront.net/hls/live.m3u8';
```

### Metadata API
Metadata is fetched from:
```
https://d3d4yli4hf5bmh.cloudfront.net/metadatav2.json
```

### Secret Key
**Important:** Change the Flask secret key in production!
```python
# app.py
app.secret_key = 'neoradio-secret-key-change-in-production'
```

## User Identification

The rating system uses IP-based fingerprinting to prevent duplicate votes:
1. Extracts client IP (handles X-Forwarded-For for proxies)
2. Combines with User-Agent string
3. Creates SHA256 hash for privacy
4. Uses first 32 characters as user_id

This approach:
- Prevents cookie clearing exploits
- Maintains user privacy through hashing
- Persists across browser sessions

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
