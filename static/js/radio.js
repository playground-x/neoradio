const streamUrl = 'https://d3d4yli4hf5bmh.cloudfront.net/hls/live.m3u8';
const audio = document.getElementById('audio');
const statusEl = document.getElementById('status');
const playBtn = document.getElementById('playBtn');
const stopBtn = document.getElementById('stopBtn');
const connectionStatus = document.getElementById('connectionStatus');
let hls;
let trackHistory = [];
let currentTrack = null;

// Initialize visualizer bars
const visualizer = document.getElementById('visualizer');
const barCount = 40;
for (let i = 0; i < barCount; i++) {
    const bar = document.createElement('div');
    bar.className = 'bar';
    visualizer.appendChild(bar);
}

function updateStatus(message, className) {
    statusEl.textContent = message;
    statusEl.className = 'status ' + className;
}

function playStream() {
    if (Hls.isSupported()) {
        updateStatus('Loading stream...', 'loading');

        if (hls) {
            hls.destroy();
        }

        hls = new Hls({
            enableWorker: true,
            lowLatencyMode: false,
            backBufferLength: 90,
            enableID3MetadataCues: true,
            enableWebVTT: true,
            enableCEA708Captions: false
        });

        hls.loadSource(streamUrl);
        hls.attachMedia(audio);

        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            audio.play().then(() => {
                updateStatus('▶ Now Playing - Live Stream', 'playing');
                connectionStatus.textContent = 'Connected';
                connectionStatus.style.color = '#28a745';
                playBtn.disabled = true;
                stopBtn.disabled = false;
                startVisualizer();
                updateAudioQuality();

                // Initialize with default track info
                updateTrackInfo({});

                // Start polling for metadata
                startMetadataPolling();
            }).catch(error => {
                updateStatus('Error: Could not play stream', 'error');
                console.error('Playback error:', error);
            });
        });

        hls.on(Hls.Events.LEVEL_SWITCHED, function(event, data) {
            updateAudioQuality(data.level);
        });

        // Listen for ID3 metadata tags (track info)
        hls.on(Hls.Events.FRAG_PARSING_METADATA, function(event, data) {
            console.log('=== METADATA EVENT ===');
            console.log('Full event data:', JSON.stringify(data, null, 2));
            console.log('Raw metadata object:', data);

            if (data.samples && data.samples.length > 0) {
                data.samples.forEach((sample, index) => {
                    console.log(`Sample ${index}:`, sample);
                    console.log(`Sample type:`, sample.type);
                    console.log(`Sample data:`, sample.data);

                    if (sample.data) {
                        console.log('Data keys:', Object.keys(sample.data));
                        console.log('Full data object:', JSON.stringify(sample.data, null, 2));

                        // Log each property
                        for (let key in sample.data) {
                            const value = sample.data[key];
                            console.log(`  ${key}:`, value);
                            if (typeof value === 'object') {
                                console.log(`    ${key} type:`, typeof value);
                                console.log(`    ${key} keys:`, Object.keys(value));
                                console.log(`    ${key} full:`, JSON.stringify(value, null, 2));
                            }
                        }

                        parseID3Metadata(sample.data);
                    }
                });
            }
            console.log('=== END METADATA ===');
        });

        // Also listen for all HLS events to debug
        hls.on(Hls.Events.FRAG_LOADED, function(event, data) {
            console.log('Fragment loaded, checking for metadata...');
        });

        hls.on(Hls.Events.ERROR, function(event, data) {
            if (data.fatal) {
                switch(data.type) {
                    case Hls.ErrorTypes.NETWORK_ERROR:
                        updateStatus('Network error - trying to recover...', 'error');
                        hls.startLoad();
                        break;
                    case Hls.ErrorTypes.MEDIA_ERROR:
                        updateStatus('Media error - trying to recover...', 'error');
                        hls.recoverMediaError();
                        break;
                    default:
                        updateStatus('Fatal error - cannot recover', 'error');
                        hls.destroy();
                        break;
                }
            }
        });

    } else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        audio.src = streamUrl;

        // Listen for metadata in Safari
        audio.addEventListener('loadedmetadata', function() {
            console.log('Native HLS metadata loaded');
            if (audio.textTracks) {
                for (let i = 0; i < audio.textTracks.length; i++) {
                    const track = audio.textTracks[i];
                    if (track.kind === 'metadata') {
                        track.addEventListener('cuechange', function() {
                            const cue = track.activeCues[0];
                            if (cue && cue.value) {
                                console.log('Cue metadata:', cue.value);
                                parseID3Metadata(cue.value);
                            }
                        });
                    }
                }
            }
        });

        audio.play().then(() => {
            updateStatus('▶ Now Playing - Live Stream', 'playing');
            connectionStatus.textContent = 'Connected';
            connectionStatus.style.color = '#28a745';
            playBtn.disabled = true;
            stopBtn.disabled = false;
            startVisualizer();
            updateAudioQuality();

            // Initialize with default track info
            updateTrackInfo({});

            // Start polling for metadata
            startMetadataPolling();
        }).catch(error => {
            updateStatus('Error: Could not play stream', 'error');
            console.error('Playback error:', error);
        });
    } else {
        updateStatus('Error: HLS not supported in this browser', 'error');
    }
}

function stopStream() {
    audio.pause();
    audio.currentTime = 0;

    if (hls) {
        hls.destroy();
        hls = null;
    }

    updateStatus('Stream stopped', '');
    connectionStatus.textContent = 'Disconnected';
    connectionStatus.style.color = '#666';
    playBtn.disabled = false;
    stopBtn.disabled = true;
    stopVisualizer();
    stopMetadataPolling();
}

function changeVolume(value) {
    audio.volume = value / 100;
    document.getElementById('volumeValue').textContent = value;
}

// Simple visualizer animation
let visualizerInterval;

function startVisualizer() {
    const bars = document.querySelectorAll('.bar');
    visualizerInterval = setInterval(() => {
        bars.forEach(bar => {
            const height = Math.random() * 40 + 10;
            bar.style.height = height + 'px';
        });
    }, 150);
}

function stopVisualizer() {
    if (visualizerInterval) {
        clearInterval(visualizerInterval);
        const bars = document.querySelectorAll('.bar');
        bars.forEach(bar => {
            bar.style.height = '5px';
        });
    }
}

// Handle audio events
audio.addEventListener('waiting', () => {
    updateStatus('Buffering...', 'loading');
});

audio.addEventListener('playing', () => {
    updateStatus('▶ Now Playing - Live Stream', 'playing');
});

audio.addEventListener('pause', () => {
    if (!audio.ended) {
        updateStatus('Paused', '');
    }
});

audio.addEventListener('ended', () => {
    stopStream();
});

// Set initial volume
audio.volume = 1.0;

// Poll for metadata from API (fallback if HLS doesn't have embedded metadata)
let metadataPollingInterval = null;

function startMetadataPolling() {
    // Poll every 10 seconds
    metadataPollingInterval = setInterval(fetchMetadataFromAPI, 10000);
    // Fetch immediately
    fetchMetadataFromAPI();
}

function stopMetadataPolling() {
    if (metadataPollingInterval) {
        clearInterval(metadataPollingInterval);
        metadataPollingInterval = null;
    }
}

async function fetchMetadataFromAPI() {
    try {
        const response = await fetch('/api/metadata');
        if (!response.ok) {
            // No metadata API available - this is expected
            return;
        }

        const data = await response.json();
        console.log('API metadata response:', data);

        if (data.data) {
            // Parse the API response
            parseAPIMetadata(data.data);
        }
    } catch (error) {
        // Silently fail - no metadata API available
        console.log('No metadata API available');
    }
}

function parseAPIMetadata(data) {
    console.log('Parsing API metadata:', data);

    const track = {};

    // Extract current track info from metadatav2.json format
    if (data.title) track.title = data.title;
    if (data.artist) track.artist = data.artist;
    if (data.album) track.album = data.album;
    if (data.date) track.year = data.date;

    // Only update if we have at least a title or artist
    if (track.title || track.artist) {
        console.log('Track data from API:', track);
        updateTrackInfo(track);
    } else {
        console.log('No track data found in metadata');
    }
}

// Parse ID3 metadata from HLS stream
function parseID3Metadata(metadata) {
    if (!metadata) {
        console.log('No metadata provided');
        return;
    }

    console.log('Parsing metadata:', metadata);
    const track = {};
    let hasData = false;

    // Handle different metadata formats
    // Check if metadata is an object with properties
    if (typeof metadata === 'object') {
        // ID3 tags common in streaming (case-insensitive check)
        const keys = Object.keys(metadata);
        console.log('Metadata keys:', keys);

        // Check for common ID3 tags
        for (let key of keys) {
            const upperKey = key.toUpperCase();
            const value = metadata[key];

            // Handle different tag formats
            if (upperKey === 'TIT2' || upperKey === 'TITLE') {
                track.title = value.data || value;
                hasData = true;
            }
            if (upperKey === 'TPE1' || upperKey === 'ARTIST') {
                track.artist = value.data || value;
                hasData = true;
            }
            if (upperKey === 'TALB' || upperKey === 'ALBUM') {
                track.album = value.data || value;
                hasData = true;
            }
            if (upperKey === 'TDRC' || upperKey === 'TYER' || upperKey === 'YEAR') {
                track.year = value.data || value;
                hasData = true;
            }

            // StreamTitle format (common in Icecast/Shoutcast)
            if (upperKey === 'STREAMTITLE' || key === 'StreamTitle') {
                const streamTitle = value.data || value;
                console.log('StreamTitle found:', streamTitle);
                // Parse "Artist - Title" format
                const parts = streamTitle.split(' - ');
                if (parts.length >= 2) {
                    track.artist = parts[0].trim();
                    track.title = parts.slice(1).join(' - ').trim();
                } else {
                    track.title = streamTitle;
                }
                hasData = true;
            }

            // TXXX frames (custom tags)
            if (upperKey === 'TXXX') {
                console.log('TXXX frame:', value);
            }
        }
    }

    if (hasData) {
        console.log('Track data extracted:', track);
        updateTrackInfo(track);
    } else {
        console.log('No track data found in metadata');
    }
}

// Update track information from metadata
function updateTrackInfo(trackData) {
    const track = {
        title: trackData.title || 'Live Stream',
        artist: trackData.artist || 'NeoRadio',
        album: trackData.album || 'Live Broadcast',
        year: trackData.year || new Date().getFullYear()
    };

    document.getElementById('trackTitle').textContent = track.title;
    document.getElementById('trackArtist').textContent = track.artist;
    document.getElementById('trackAlbum').textContent = track.album;
    document.getElementById('trackYear').textContent = track.year;

    // Only add to history if we have actual track data (not default placeholder values)
    const hasRealData = trackData.title || trackData.artist;

    // Add to history if it's a new track and has real data
    if (hasRealData && (!currentTrack || currentTrack.title !== track.title || currentTrack.artist !== track.artist)) {
        currentTrack = track;
        addToHistory(track);

        // Refresh album art with cache-busting timestamp
        const albumArt = document.getElementById('albumArt');
        albumArt.src = `https://d3d4yli4hf5bmh.cloudfront.net/cover.jpg?t=${Date.now()}`;

        // Load rating for this track
        loadSongRating(track.title, track.artist);
    } else if (hasRealData) {
        // Even if not new, load rating on initial load
        loadSongRating(track.title, track.artist);
    }
}

// Add track to history
function addToHistory(track) {
    const historyItem = {
        ...track,
        timestamp: new Date()
    };

    trackHistory.unshift(historyItem);

    // Keep only last 10 tracks
    if (trackHistory.length > 10) {
        trackHistory = trackHistory.slice(0, 10);
    }

    updateHistoryDisplay();
}

// Update history display
function updateHistoryDisplay() {
    const historyContainer = document.getElementById('trackHistory');

    if (trackHistory.length === 0) {
        historyContainer.innerHTML = '<div class="empty-history">No track history yet. Start playing to see recent tracks.</div>';
        return;
    }

    historyContainer.innerHTML = trackHistory.map(track => `
        <div class="history-item">
            <div class="history-track">${track.title}</div>
            <div class="history-artist">${track.artist}</div>
            <div class="history-time">${track.album} • ${track.year} • ${formatTime(track.timestamp)}</div>
        </div>
    `).join('');
}

// Format timestamp
function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

// Update audio quality information
function updateAudioQuality(levelIndex) {
    if (hls && hls.levels && hls.levels.length > 0) {
        const level = levelIndex !== undefined ? hls.levels[levelIndex] : hls.levels[hls.currentLevel];

        if (level) {
            // Extract codec info
            const codec = level.audioCodec || 'AAC';
            document.getElementById('audioCodec').textContent = codec.toUpperCase();

            // Bitrate
            const bitrate = level.bitrate ? Math.round(level.bitrate / 1000) + ' kbps' : 'Variable';
            document.getElementById('bitrate').textContent = bitrate;
        }
    }

    // Try to get audio track info from the audio element
    if (audio.audioTracks && audio.audioTracks.length > 0) {
        const track = audio.audioTracks[0];
        console.log('Audio track info:', track);
    }

    // Set sample rate and channels (common for lossless)
    document.getElementById('sampleRate').textContent = '48 kHz';
    document.getElementById('channels').textContent = 'Stereo (2.0)';
}

// Load initial track metadata on page load
async function loadInitialMetadata() {
    try {
        const response = await fetch('/api/metadata');
        if (response.ok) {
            const data = await response.json();
            if (data.data) {
                parseAPIMetadata(data.data);
            }
        }
    } catch (error) {
        console.log('Could not load initial metadata:', error);
    }
}

// Load metadata when page loads
loadInitialMetadata();

// Rating functionality
async function rateSong(rating) {
    if (!currentTrack || currentTrack.title === 'Live Stream') {
        alert('Please wait for track information to load before rating.');
        return;
    }

    try {
        const response = await fetch('/api/songs/rating', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: currentTrack.title,
                artist: currentTrack.artist,
                album: currentTrack.album,
                year: currentTrack.year,
                rating: rating
            })
        });

        if (response.ok) {
            const data = await response.json();
            updateRatingDisplay(data.thumbs_up, data.thumbs_down, rating);
        } else {
            console.error('Failed to submit rating');
        }
    } catch (error) {
        console.error('Error submitting rating:', error);
    }
}

async function loadSongRating(title, artist) {
    try {
        const response = await fetch(`/api/songs/rating/${encodeURIComponent(title)}/${encodeURIComponent(artist)}`);
        if (response.ok) {
            const data = await response.json();
            updateRatingDisplay(data.thumbs_up, data.thumbs_down, data.user_rating);
        }
    } catch (error) {
        console.error('Error loading rating:', error);
        updateRatingDisplay(0, 0, null);
    }
}

function updateRatingDisplay(thumbsUp, thumbsDown, userRating) {
    document.getElementById('thumbsUpCount').textContent = thumbsUp;
    document.getElementById('thumbsDownCount').textContent = thumbsDown;

    const thumbsUpBtn = document.getElementById('thumbsUpBtn');
    const thumbsDownBtn = document.getElementById('thumbsDownBtn');

    // Remove active class from both
    thumbsUpBtn.classList.remove('active');
    thumbsDownBtn.classList.remove('active');

    // Add active class to user's rating
    if (userRating === 1) {
        thumbsUpBtn.classList.add('active');
    } else if (userRating === -1) {
        thumbsDownBtn.classList.add('active');
    }
}
