"""
Tests for Flask route endpoints.
"""

import pytest
import json


class TestRadioRoute:
    """Tests for the radio player route."""

    def test_radio_page_loads(self, client):
        """Test that the radio page loads successfully."""
        response = client.get('/radio')
        assert response.status_code == 200
        assert b'NeoRadio' in response.data

    def test_radio_page_has_player_elements(self, client):
        """Test that the radio page contains required player elements."""
        response = client.get('/radio')
        assert b'id="audio"' in response.data
        assert b'id="playBtn"' in response.data
        assert b'id="stopBtn"' in response.data
        assert b'id="visualizer"' in response.data

    def test_radio_page_has_rating_buttons(self, client):
        """Test that the radio page contains rating functionality."""
        response = client.get('/radio')
        assert b'id="thumbsUpBtn"' in response.data
        assert b'id="thumbsDownBtn"' in response.data
        assert b'thumbsUpCount' in response.data
        assert b'thumbsDownCount' in response.data


class TestMetadataAPI:
    """Tests for the metadata API endpoint."""

    def test_metadata_endpoint_exists(self, client):
        """Test that the metadata endpoint is accessible."""
        response = client.get('/api/metadata')
        # Should return either metadata or an error (both are valid)
        assert response.status_code in [200, 500]

    def test_metadata_returns_json(self, client):
        """Test that metadata endpoint returns JSON."""
        response = client.get('/api/metadata')
        assert response.content_type == 'application/json'


class TestRatingsAPI:
    """Tests for the song ratings API."""

    def test_rate_song_requires_data(self, client):
        """Test that rating endpoint requires proper data."""
        response = client.post('/api/songs/rating',
                                json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_rate_song_validates_rating_value(self, client):
        """Test that rating value must be 1 or -1."""
        response = client.post('/api/songs/rating',
                                json={
                                    'title': 'Test Song',
                                    'artist': 'Test Artist',
                                    'album': 'Test Album',
                                    'year': '2025',
                                    'rating': 5  # Invalid
                                })
        assert response.status_code == 400

    def test_rate_song_thumbs_up(self, client):
        """Test successful thumbs up rating."""
        response = client.post('/api/songs/rating',
                                json={
                                    'title': 'Test Song',
                                    'artist': 'Test Artist',
                                    'album': 'Test Album',
                                    'year': '2025',
                                    'rating': 1
                                })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['thumbs_up'] == 1
        assert data['thumbs_down'] == 0

    def test_rate_song_thumbs_down(self, client):
        """Test successful thumbs down rating."""
        response = client.post('/api/songs/rating',
                                json={
                                    'title': 'Another Song',
                                    'artist': 'Another Artist',
                                    'album': 'Another Album',
                                    'year': '2025',
                                    'rating': -1
                                })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['thumbs_up'] == 0
        assert data['thumbs_down'] == 1

    def test_rate_song_update_existing(self, client):
        """Test that users can update their rating."""
        song_data = {
            'title': 'Update Test',
            'artist': 'Update Artist',
            'album': 'Update Album',
            'year': '2025'
        }

        # First rating: thumbs up
        response1 = client.post('/api/songs/rating',
                                 json={**song_data, 'rating': 1})
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1['thumbs_up'] == 1

        # Update to thumbs down (same user)
        response2 = client.post('/api/songs/rating',
                                 json={**song_data, 'rating': -1})
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['thumbs_up'] == 0
        assert data2['thumbs_down'] == 1

    def test_get_song_rating_new_song(self, client):
        """Test getting ratings for a song that hasn't been rated."""
        response = client.get('/api/songs/rating/Nonexistent/Artist')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['thumbs_up'] == 0
        assert data['thumbs_down'] == 0
        assert data['user_rating'] is None

    def test_get_song_rating_existing(self, client):
        """Test getting ratings for a rated song."""
        # Rate a song first
        client.post('/api/songs/rating',
                    json={
                        'title': 'Rated Song',
                        'artist': 'Rated Artist',
                        'album': 'Rated Album',
                        'year': '2025',
                        'rating': 1
                    })

        # Get the rating
        response = client.get('/api/songs/rating/Rated%20Song/Rated%20Artist')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['thumbs_up'] == 1
        assert data['thumbs_down'] == 0
        assert data['user_rating'] == 1
