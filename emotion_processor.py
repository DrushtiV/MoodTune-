import cv2
import numpy as np
from deepface import DeepFace
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self):
        # Pre-load the model to avoid delays during first prediction
        logger.info("Initializing DeepFace Emotion Model...")
        try:
            # This triggers the model download/loading
            DeepFace.build_model("Emotion")
        except Exception as e:
            logger.error(f"Error initializing DeepFace: {e}")

    def analyze_emotion(self, image_array):
        """
        Analyzes the emotion from an image array (numpy).
        Returns the dominant emotion.
        """
        try:
            # DeepFace expects BGR for OpenCV or RGB. Streamlit provides RGB.
            # Convert RGB to BGR for standard processing
            img_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Analyze using DeepFace
            results = DeepFace.analyze(
                img_path=img_bgr, 
                actions=['emotion'],
                enforce_detection=False, # Don't crash if face not detected
                detector_backend='opencv'
            )
            
            if results:
                # DeepFace returns a list of dicts (one for each face)
                dominant_emotion = results[0]['dominant_emotion']
                return dominant_emotion
            return "neutral"
        
        except Exception as e:
            logger.error(f"Emotion analysis error: {e}")
            return "neutral"

    @staticmethod
    def map_emotion_to_params(emotion):
        """
        Maps detected emotion to Spotify audio features.
        Valence: 0.0 (sad/depressed) to 1.0 (happy/cheerful)
        Energy: 0.0 (calm) to 1.0 (intense/fast)
        """
        mappings = {
            'happy': {
                'target_valence': 0.8,
                'target_energy': 0.8,
                'seed_genres': ['happy', 'pop', 'dance']
            },
            'sad': {
                'target_valence': 0.2,
                'target_energy': 0.2,
                'seed_genres': ['acoustic', 'piano', 'sad']
            },
            'angry': {
                'target_valence': 0.1,
                'target_energy': 0.9,
                'seed_genres': ['rock', 'metal', 'hardcore']
            },
            'surprise': {
                'target_valence': 0.7,
                'target_energy': 0.8,
                'seed_genres': ['electronic', 'party', 'indie-pop']
            },
            'neutral': {
                'target_valence': 0.5,
                'target_energy': 0.5,
                'seed_genres': ['ambient', 'chill', 'acoustic']
            },
            'fear': {
                'target_valence': 0.2,
                'target_energy': 0.6,
                'seed_genres': ['ambient', 'soundtrack', 'classical']
            },
            'disgust': {
                'target_valence': 0.3,
                'target_energy': 0.4,
                'seed_genres': ['grunge', 'blues', 'alternative']
            }
        }
        return mappings.get(emotion, mappings['neutral'])
