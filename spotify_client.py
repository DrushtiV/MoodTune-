import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

class SpotifyRecommender:
    def __init__(self):
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise ValueError("Spotify Credentials not found in environment variables.")

        auth_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_recommendations(self, emotion_params, limit=10):
        """
        Fetches tracks from Spotify based on audio feature targets.
        """
        try:
            results = self.sp.recommendations(
                seed_genres=emotion_params['seed_genres'],
                target_valence=emotion_params['target_valence'],
                target_energy=emotion_params['target_energy'],
                limit=limit
            )
            
            tracks = []
            for track in results['tracks']:
                tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album_art': track['album']['images'][0]['url'],
                    'external_url': track['external_urls']['spotify'],
                    'preview_url': track['preview_url']
                })
            return tracks
        except Exception as e:
            print(f"Spotify API Error: {e}")
            return []
