import unittest
from project import (
    get_access_token,
    create_playlist,
    search_songs,
    get_youtube_client,
    get_playlists,
    get_videos_from_playlist,
    get_artist_and_track_from_video,
    Song
)

def test_get_access_token(unittest.TestCase):
    access_token = get_access_token()
    unittest.TestCase.assertIsNotNone(access_token)
    unittest.TestCase.assertTrue(access_token.startswith('Bearer '))

def test_create_playlist(unittest.TestCase):
    user_id = "test_user_id"
    token = "test_access_token"
    playlist_id = create_playlist(user_id, token)
    unittest.TestCase.assertIsNotNone(playlist_id)

def test_search_songs(unittest.TestCase):
    test_song = Song("Test Song")
    uri = search_songs(test_song)
    unittest.TestCase.assertIsNotNone(uri)

def test_get_youtube_client(unittest.TestCase):
    youtube_client = get_youtube_client()
    unittest.TestCase.assertIsNotNone(youtube_client)

