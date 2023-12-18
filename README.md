# SyncWave: YTMusic to Spotify
! [screenshot of the gui app] (assets/frame0/app.jpg)
#### Video Demo: 
##### CLI APP: https://youtu.be/nVkyocuU2e8
##### GUI APP: https://youtu.be/_aOAsLIk6TM
#### Description: 
# YouTube to Spotify Playlist Converter

This Python script allows you to convert YouTube playlists into Spotify playlists seamlessly. It uses the YouTube Data API v3 to fetch videos from a given YouTube playlist and then searches for corresponding tracks on Spotify. The matching tracks are added to a new Spotify playlist specified by the user.

## Prerequisites

Before you run the script, you'll need to set up a few things:

1. **YouTube Data API v3:** Create a project on the [Google Cloud Console](https://console.developers.google.com/) and enable the YouTube Data API v3 for your project. Obtain the client secrets file and set up an environment variable with the location of the client secrets file.

2. **Spotify Developer Account:** Create an application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) to get your Spotify Client ID and Client Secret. Set up the redirect URI to `http://localhost:8888/callback` in your Spotify application settings.

3. **Environment Variables:** Set up the following environment variables with your Spotify Client ID, Client Secret and Youtube Client Secrets file:

   ```
   export YOUR_APP_CLIENT_ID='YOUR_SPOTIFY_CLIENT_ID'
   export YOUR_APP_CLIENT_SECRET='YOUR_SPOTIFY_CLIENT_SECRET'
   export SPOTIFY_REDIRECT_URI='http://localhost:8888/callback'
   export YT_CLIENT_SECRETS='location of your YT_CLIENT_SECRETS file'
   export ASSETS_LOCATION='location of your ASSETS folder'
   ```

4. **Dependencies:** Install the required Python packages using `pip`:

   ```
   pip install -r requirements.txt
   ```

## How to Use

1. Run the script using Python 3:

   for CLI app:
   ```
   python project.py
   ```
   for GUI app:
   ```
   python final_project.py
   ```

2. You will be prompted to enter your YouTube playlist URL. Provide the URL of the YouTube playlist you want to convert.

3. The script will fetch videos from the YouTube playlist, search for matching tracks on Spotify, and create a new private Spotify playlist. The Spotify playlist URL will be displayed once the process is complete.

## Additional Notes

- The script utilizes the `requests` library for Spotify API interactions and `yt_dlp` for extracting video information from YouTube playlists.
- Ensure your YouTube videos have accurate titles to improve the matching accuracy with Spotify tracks.
- Be mindful of the rate limits of the YouTube Data API and Spotify API to avoid getting blocked.

TODO: Make it a web app
