import json
import requests
import os

import youtube_dl as yt_dlp

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def get_access_token():

    CLIENT_ID = "Client_ID" # Provided by spotify
    CLIENT_SECRET = "CLIENT_SECRET" # Also provided by spotify. Not meant to be shared in source code.
    # URLS
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    BASE_URL = 'https://api.spotify.com/v1/'


    # Make a request to the /authorize endpoint to get an authorization code
    auth_code = requests.get(AUTH_URL, {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': 'http://localhost:8888/callback',
        'scope': 'playlist-modify-private',
    })
    print(f"Click the link and follow through:", auth_code.url, sep='\n')
    code = input("Enter the redirected url: ")
    code = code[code.find('=')+1:]
    

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:8888/callback',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    # Make a request to the /token endpoint to get an access token
    access_token_request = requests.post(url=TOKEN_URL, data=payload)

    # convert the response to JSON
    access_token_response_data = access_token_request.json()

    # save the access token
    access_token = access_token_response_data['access_token']
    
    return access_token
# get user's spotify user id
user_id = input("Enter your user ID: ")
# get user's access token
token = get_access_token()

def main():
    youtube_client = get_youtube_client()
    sp_playlist_id = create_playlist(user_id, token)
    playlists = get_playlists(youtube_client)

    for index, playlist in enumerate(playlists):
        print(index, playlist.title)

    choice = int(input("Select a playlist: "))
    chosen = playlists[choice]
    print(f"You have chosen {chosen.title}")
    songs = get_videos_from_playlist(youtube_client, chosen.id)
    uris = []
    for song in songs:
        uris.append(search_songs(song))

    query = f"https://api.spotify.com/v1/playlists/{sp_playlist_id}/tracks"
    request_data = json.dumps(uris)

    response = requests.post(
        query,
        data=request_data,
        headers={
            "Content-Type":"application/json",
            "Authorization":f"Bearer {token}"
        }
    )
    response_json = response.json()
    return response_json

# Playlist class with id and title attributes
class Playlist(object):
    def __init__(self, id, title) -> None:
        self.id = id
        self.title = title

# Song class with title attribute
class Song(object):
    def __init__(self, title) -> None:
       self.title = title


def create_playlist(user_id, token):
    # Prompts the user to add name and description to their playlist
    name = input("What would you like to call your playlist? ")
    desc = input("Enter the description for your playlist: ")
    request_body = json.dumps(
    {
        "name": name,
        "description": desc,
        "public": False
    }
    )

    query = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    response = requests.post(
        query,
        data=request_body,
        headers={
            "Content-Type":"application/json",
            "Authorization":f"Bearer {token}"
        }
    )
    response_json = response.json()
    return response_json["id"]


def search_songs(Song):
    Song.title.replace(' ','%2520')
    print(Song.title)
    query = f"https://api.spotify.com/v1/search?query={Song.title}&type=track&offset=0&limit=10"

    response = requests.get(
        query,
        headers={
            "Content-Type":"application/json",
            "Authorization":f"Bearer {token}"
        }
    )
    response_json = response.json()
    songs = response_json['tracks']['items']

    uri = songs[0]['uri']
    return uri


def get_youtube_client():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json" # Path to your yt client_secrets js object. not meant to be revealed.

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server()
    youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    return youtube_client
    
def get_playlists(youtube_client):
    request = youtube_client.playlists().list(
        part="id, snippet",
        maxResults=50,
        mine=True,
    )

    response = request.execute()

    playlists = [Playlist(item['id'], item['snippet']['title'] ) for item in response['items']]

    return playlists

def get_videos_from_playlist(youtube_client, playlist_id):
    songs = []
    request = youtube_client.playlistItems().list(
        part='id, snippet',
        playlistId = playlist_id,
    )

    response = request.execute()

    for item in response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        title = get_artist_and_track_from_video(video_id)
        if title:
            songs.append(Song(title))

    return songs


def get_artist_and_track_from_video(video_id):
    youtube_url = f"https://music.youtube.com/watch?v={video_id}"

    video = yt_dlp.YoutubeDL({'quiet':True}).extract_info(
        youtube_url, download=False
    )
    
    try:
        title = video['title']
    except ValueError:
        title = None

    return title



if __name__ == '__main__':
    main()
