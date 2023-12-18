from pathlib import Path
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Toplevel
import json
import requests
import os
import youtube_dl as yt_dlp
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import webbrowser


youtube_client = None
access_token = None
sp_playlist_id = None
playlists = None

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"/Users/dhanushm/Documents/python_projects/yt2spotify/assets/frame0")


# Playlist class with id and title attributes
class Playlist(object):
    def __init__(self, id, title) -> None:
        self.id = id
        self.title = title
# Song class with title attribute
class Song(object):
    def __init__(self, title) -> None:
       self.title = title

def get_user_id(event = None):
    
    global user_id
    global code
      # get user's spotify user id
    user_id = user_id.get()
    print(user_id)

    CLIENT_ID = "ca4be83d92324632bfed6c87a057864d" # Provided by spotify
    CLIENT_SECRET = "a5ca84951f5a4cf4932b4ff84c290f56" # Also provided by spotify. Not meant to be shared in source code.
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
    webbrowser.open_new(auth_code.url)

def get_youtube_client():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "/Users/dhanushm/Documents/python_projects/yt2spotify/client_secrets.json" # Path to your yt client_secrets js object. not meant to be revealed.

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server()
    global youtube_client
    youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

def get_access_token():
    global user_id
    global code

    CLIENT_ID = "ca4be83d92324632bfed6c87a057864d" # Provided by spotify
    CLIENT_SECRET = "a5ca84951f5a4cf4932b4ff84c290f56" # Also provided by spotify. Not meant to be shared in source code.
    # URLS
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    BASE_URL = 'https://api.spotify.com/v1/'


    code = code.get()
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
    global access_token
    access_token = access_token_response_data['access_token']
    print(access_token)

def create_playlist(event = None):
    # Prompts the user to add name and description to their playlist
    global user_id
    global access_token
    global name
    global desc
    name = name.get()
    desc = desc.get()
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
            "Authorization":f"Bearer {access_token}"
        }
    )
    response_json = response.json()
    print(response_json)
    global sp_playlist_id 
    sp_playlist_id = response_json["id"]

def search_songs(Song):
    Song.title.replace(' ','%2520')
    print(Song.title)
    query = f"https://api.spotify.com/v1/search?query={Song.title}&type=track&offset=0&limit=10"

    response = requests.get(
        query,
        headers={
            "Content-Type":"application/json",
            "Authorization":f"Bearer {access_token}"
        }
    )
    response_json = response.json()
    songs = response_json['tracks']['items']

    uri = songs[0]['uri']
    return uri

def get_playlists():
    global playlists
    global youtube_client
    request = youtube_client.playlists().list(
        part="id, snippet",
        maxResults=50,
        mine=True,
    )

    response = request.execute()

    playlists = [Playlist(item['id'], item['snippet']['title'] ) for item in response['items']]

    playlists_window = Toplevel(window)
    playlists_window.title("Playlists")
    playlists_window.geometry("1280x720")
    for index, playlist in enumerate(playlists):
        tk.Label(playlists_window, text= f"{index} {playlist.title}").place(x=50, y = (index + 1) *  50)

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

def generate():
    global youtube_client
    global access_token
    global choice
    global sp_playlist_id

    choice = int(choice.get())
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
            "Authorization":f"Bearer {access_token}"
        }
    )
    response_json = response.json()
    return response_json

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1674x881")
window.title("SyncWave")
window.configure(bg = "#FFFFFF")

user_id = tk.StringVar()
code = tk.StringVar()
choice = tk.StringVar()
name = tk.StringVar()
desc = tk.StringVar()

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 881,
    width = 1674,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    837.0,
    440.0,
    image=image_image_1
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=generate,
    relief="flat"
)
button_1.place(
    x=961.0,
    y=639.0,
    width=396.0,
    height=89.0
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=get_playlists,
    relief="flat"
)
button_4.place(
    x=961.0,
    y=379.0,
    width=396.0,
    height=89.0
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    1223.5,
    556.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000000",
    textvariable=choice,
    highlightthickness=0
)
entry_1.place(
    x=1083.0,
    y=530.0,
    width=281.0,
    height=51.0
)

canvas.create_text(
    808.0,
    197.0,
    anchor="nw",
    text="Playlist name: ",
    fill="#FFFFFF",
    font=("Inter", 35 * -1)
)

canvas.create_text(
    686.0,
    9.0,
    anchor="nw",
    text="SyncWave",
    fill="#FFFFFF",
    font=("Inter", 54 * -1)
)

canvas.create_rectangle(
    563.0,
    71.99999994096277,
    1051.999988044703,
    75.0,
    fill="#000000",
    outline="")

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=get_youtube_client,
    relief="flat"
)
button_2.place(
    x=69.0,
    y=134.0,
    width=396.0,
    height=89.0
)

canvas.create_text(
    69.0,
    264.0,
    anchor="nw",
    text="Enter your Spotify user ID:",
    fill="#FFFFFF",
    font=("Inter", 35 * -1)
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    371.0,
    587.5,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000000",
    textvariable=code,
    highlightthickness=0
)
entry_2.place(
    x=69.0,
    y=548.0,
    width=604.0,
    height=77.0
)

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    371.0,
    371.5,
    image=entry_image_3
)
entry_3 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000000",
    textvariable=user_id,
    highlightthickness=0
)
entry_3.bind('<Return>', get_user_id)
entry_3.place(
    x=69.0,
    y=332.0,
    width=604.0,
    height=77.0
)

canvas.create_text(
    66.0,
    484.0,
    anchor="nw",
    text="Enter the redirected link:",
    fill="#FFFFFF",
    font=("Inter", 35 * -1)
)

canvas.create_rectangle(
    755.9999685277978,
    103.0,
    757.0,
    824.0,
    fill="#000000",
    outline="")

entry_image_4 = PhotoImage(
    file=relative_to_assets("entry_4.png"))
entry_bg_4 = canvas.create_image(
    1356.5,
    218.5,
    image=entry_image_4
)
entry_4 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000000",
    textvariable=name,
    highlightthickness=0
)
entry_4.place(
    x=1083.0,
    y=196.0,
    width=547.0,
    height=43.0
)

entry_image_5 = PhotoImage(
    file=relative_to_assets("entry_5.png"))
entry_bg_5 = canvas.create_image(
    1356.5,
    308.5,
    image=entry_image_5
)
entry_5 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000000",
    textvariable=desc,
    highlightthickness=0
)
entry_5.bind("<Return>", create_playlist)
entry_5.place(
    x=1083.0,
    y=286.0,
    width=547.0,
    height=43.0
)

canvas.create_text(
    768.0,
    282.0,
    anchor="nw",
    text="Playlist description: ",
    fill="#FFFFFF",
    font=("Inter", 35 * -1)
)

canvas.create_text(
    833.0,
    539.0,
    anchor="nw",
    text="Select playlist:",
    fill="#FFFFFF",
    font=("Inter", 35 * -1)
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=get_access_token,
    relief="flat"
)
button_3.place(
    x=74.0,
    y=655.0,
    width=396.0,
    height=89.0
)

canvas.pack()
window.resizable(False, False)
window.mainloop()

