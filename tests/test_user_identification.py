"""
Tests for user identification system.
"""

import pytest
import json
import hashlib


class TestIPBasedUserIdentification:
    """Tests for IP + User-Agent fingerprinting."""

    def test_same_ip_same_user_agent_same_id(self, client):
        """Test that same IP and User-Agent produce same user ID."""
        song_data = {
            'title': 'ID Test Song',
            'artist': 'ID Test Artist',
            'album': 'Album',
            'year': '2025',
            'rating': 1
        }

        # First rating
        response1 = client.post('/api/songs/rating',
                                 json=song_data,
                                 headers={'User-Agent': 'TestBrowser/1.0'})
        assert response1.status_code == 200

        # Second rating (should update, not create new)
        song_data['rating'] = -1
        response2 = client.post('/api/songs/rating',
                                 json=song_data,
                                 headers={'User-Agent': 'TestBrowser/1.0'})
        assert response2.status_code == 200

        # Check that rating was updated (not duplicated)
        data = json.loads(response2.data)
        assert data['thumbs_down'] == 1
        assert data['thumbs_up'] == 0

    def test_different_user_agent_different_rating(self, client):
        """Test that different User-Agent allows separate rating."""
        song_data = {
            'title': 'Multi User Test',
            'artist': 'Multi Artist',
            'album': 'Album',
            'year': '2025',
            'rating': 1
        }

        # First user (Browser 1)
        response1 = client.post('/api/songs/rating',
                                 json=song_data,
                                 headers={'User-Agent': 'Browser/1.0'})
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1['thumbs_up'] == 1

        # Second user (Browser 2) - different User-Agent
        song_data['rating'] = -1
        response2 = client.post('/api/songs/rating',
                                 json=song_data,
                                 headers={'User-Agent': 'Browser/2.0'})
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        # Both ratings should exist
        assert data2['thumbs_up'] == 1
        assert data2['thumbs_down'] == 1

    def test_user_id_hashing(self):
        """Test that user IDs are properly hashed."""
        ip = '127.0.0.1'
        user_agent = 'TestBrowser/1.0'
        identifier_string = f"{ip}:{user_agent}"
        expected_hash = hashlib.sha256(identifier_string.encode()).hexdigest()[:32]

        # Verify hash length and format
        assert len(expected_hash) == 32
        assert all(c in '0123456789abcdef' for c in expected_hash)

    def test_x_forwarded_for_header(self, client):
        """Test that X-Forwarded-For header is respected for proxied requests."""
        song_data = {
            'title': 'Proxy Test',
            'artist': 'Proxy Artist',
            'album': 'Album',
            'year': '2025',
            'rating': 1
        }

        # Request with X-Forwarded-For (simulating proxy)
        response = client.post('/api/songs/rating',
                                json=song_data,
                                headers={
                                    'User-Agent': 'TestBrowser/1.0',
                                    'X-Forwarded-For': '192.168.1.100, 10.0.0.1'
                                })
        assert response.status_code == 200

        # Same request should update (not create new)
        song_data['rating'] = -1
        response2 = client.post('/api/songs/rating',
                                 json=song_data,
                                 headers={
                                     'User-Agent': 'TestBrowser/1.0',
                                     'X-Forwarded-For': '192.168.1.100, 10.0.0.1'
                                 })
        assert response2.status_code == 200
        data = json.loads(response2.data)
        # Should have updated, not duplicated
        assert data['thumbs_down'] == 1
        assert data['thumbs_up'] == 0

    def test_get_rating_shows_user_rating(self, client):
        """Test that GET endpoint returns user's own rating."""
        # Rate a song
        client.post('/api/songs/rating',
                    json={
                        'title': 'User Rating Test',
                        'artist': 'Test Artist',
                        'album': 'Album',
                        'year': '2025',
                        'rating': 1
                    },
                    headers={'User-Agent': 'UniqueAgent/1.0'})

        # Get rating with same User-Agent
        response = client.get('/api/songs/rating/User%20Rating%20Test/Test%20Artist',
                               headers={'User-Agent': 'UniqueAgent/1.0'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_rating'] == 1

    def test_get_rating_different_user_no_rating(self, client):
        """Test that different user sees null for their rating."""
        # User 1 rates song
        client.post('/api/songs/rating',
                    json={
                        'title': 'Different User Test',
                        'artist': 'Test Artist',
                        'album': 'Album',
                        'year': '2025',
                        'rating': 1
                    },
                    headers={'User-Agent': 'UserOne/1.0'})

        # User 2 gets rating (different User-Agent)
        response = client.get('/api/songs/rating/Different%20User%20Test/Test%20Artist',
                               headers={'User-Agent': 'UserTwo/1.0'})
        assert response.status_code == 200
        data = json.loads(response.data)
        # User 2 hasn't rated yet
        assert data['user_rating'] is None
        # But can see total counts
        assert data['thumbs_up'] == 1
