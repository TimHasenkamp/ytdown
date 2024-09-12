import os
import re
import spotipy
from urllib import request as rq
from urllib.parse import quote
from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials

class Hades:
    def __init__(self):
        # Spotify API Authentifizierung
        self.__CLIENT_ID = os.environ.get("CLIENT_ID")
        self.__CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

        self.auth_manager = SpotifyClientCredentials(
            client_id=self.__CLIENT_ID, client_secret=self.__CLIENT_SECRET
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_ydl_opts(self, path):
        return {
            "format": "bestaudio/best",
            "outtmpl": f"{path}/%(id)s.%(ext)s",
            "ignoreerrors": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
        }

    def search_and_download_spotify_track(self, spotify_uri):
        # Abrufen der Track-Informationen von Spotify
        track_info = self.sp.track(spotify_uri)
        track_name = track_info['name']
        artist_name = track_info['artists'][0]['name']
        search_query = f"{track_name} {artist_name}"

        # Suche auf YouTube nach dem Track
        html = rq.urlopen(f"https://www.youtube.com/results?search_query={quote(search_query)}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        if video_ids:
            youtube_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"Found YouTube video for '{track_name}' by '{artist_name}': {youtube_url}")
            # Pfad erstellen, um den Track herunterzuladen
            path = self.create_download_directory(track_name)
            # Downloaden des Videos und Extrahieren des Audios
            with YoutubeDL(self.get_ydl_opts(path)) as ydl:
                ydl.download([youtube_url])
            print(f"Downloaded '{track_name}' by '{artist_name}' to {path}")
        else:
            print(f"No matching YouTube video found for '{track_name}' by '{artist_name}'.")

    def create_download_directory(self, dir_name):
        path = f"./downloads/{dir_name}"
        if not os.path.exists(path):
            os.makedirs(path)
        return path

if __name__ == "__main__":
    hades = Hades()
    # Beispiel Spotify-Track-URI (ersetze dies durch einen tatsächlichen Spotify-Track-URI)
    spotify_track_uri = "spotify:track:YOUR_SPOTIFY_TRACK_URI"
    hades.search_and_download_spotify_track(spotify_track_uri)
