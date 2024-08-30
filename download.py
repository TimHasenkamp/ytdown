import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

class SpotifyAPI:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                            client_secret=client_secret,
                                                            redirect_uri=redirect_uri,
                                                            scope="user-library-read"))

    def get_track_by_url(self, track_url):
        track_id = self.extract_track_id(track_url)
        track = self.sp.track(track_id)
        return {
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'spotify_url': track['external_urls']['spotify']
        }

    @staticmethod
    def extract_track_id(track_url):
        return track_url.split('/')[-1].split('?')[0]

class SongDownloader:
    def __init__(self, spotify_api):
        self.spotify_api = spotify_api

    def download_song_by_url(self, track_url):
        print(f"Fetching track from URL: {track_url}")
        track = self.spotify_api.get_track_by_url(track_url)
        
        if track:
            print(f"Found track: {track['name']} by {track['artists'][0]}")
            self.download_and_save(track)
        else:
            print(f"Track not found for URL: {track_url}")

    def download_and_save(self, track):
        song_name = track['name']
        artist = track['artists'][0]
        
        # This is where you would normally download the track from Spotify.
        # Since Spotify doesn't allow downloading directly through the API,
        # we're simulating this step.
        
        print(f"Simulating download of {song_name} by {artist}.")
        self.save_song(f"http://example.com/{song_name}.mp3", song_name)

    def save_song(self, url, song_name):
        # Simulate downloading the song
        response = requests.get(url)
        with open(f"{song_name}.mp3", 'wb') as file:
            file.write(response.content)
        print(f"Saved {song_name}.mp3")

# Setup and run the downloader
client_id = 'c3eaa588d34448ad882ef3590561db82'
client_secret = '0eb2ead801dc473d8f62fc867e4f4d83'
redirect_uri = 'http://localhost:5000/callback'

spotify_api = SpotifyAPI(client_id, client_secret, redirect_uri)
downloader = SongDownloader(spotify_api)

# Replace 'spotify_track_url' with the actual Spotify track URL
downloader.download_song_by_url('https://open.spotify.com/track/0lwyzp7GppQxv0Eu6wRkUo?si=55yzY2H_QNec0WvQBku10w')
