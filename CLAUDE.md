# NeoRadio

A modern web-based radio player for streaming HLS (HTTP Live Streaming) audio with live metadata display, track history, and community song ratings.

## Project Overview

NeoRadio is a Flask-based web application that provides a sleek, dark-themed interface for listening to live radio streams. It features real-time track metadata, album artwork, an animated visualizer, and a community-driven rating system for songs.

## Technology Stack

### Backend
- **Flask 3.1.2** - Python web framework
- **SQLite** - Database for storing songs and ratings
- **Requests 2.32.5** - HTTP library for fetching stream metadata

### Frontend
- **HLS.js** - JavaScript library for HLS stream playback
- **Vanilla JavaScript** - No framework dependencies
- **CSS Grid** - Responsive layout system

## Architecture

### File Structure

```
neoradio/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── database.db                 # SQLite database (auto-created)
├── templates/
│   ├── index.html             # Landing page
│   └── radio.html             # Radio player page
└── static/
    ├── css/
    │   └── radio.css          # Player styling
    └── js/
        └── radio.js           # Player functionality
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

### GET `/`
Landing page (requires index.html)

### GET `/radio`
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
