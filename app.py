import streamlit as st
import numpy as np
from PIL import Image
from emotion_processor import EmotionDetector
from spotify_client import SpotifyRecommender
import time

# Page Configuration
st.set_page_config(
    page_title="MoodTune - Emotion Based Music",
    page_icon="🎵",
    layout="wide"
)

# Initialize Session State
if 'emotion_detector' not in st.session_state:
    st.session_state.emotion_detector = EmotionDetector()
if 'spotify_client' not in st.session_state:
    try:
        st.session_state.spotify_client = SpotifyRecommender()
    except Exception as e:
        st.error(f"Failed to connect to Spotify: {e}")
        st.session_state.spotify_client = None

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #1DB954;
        color: white;
        border: none;
    }
    .track-card {
        background-color: #282828;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .track-card:hover {
        transform: scale(1.02);
        background-color: #3E3E3E;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🎵 MoodTune")
    st.subheader("Personalized Music Recommendations based on your Emotion")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("### 📸 Step 1: Capture your mood")
        img_file = st.camera_input("Take a photo to analyze your emotion")

        if img_file:
            # Process Image
            img = Image.open(img_file)
            img_array = np.array(img)
            
            with st.spinner("Analyzing your vibes..."):
                # Detect Emotion
                emotion = st.session_state.emotion_detector.analyze_emotion(img_array)
                st.session_state.current_emotion = emotion
                
                # Feedback
                st.success(f"Detected Emotion: **{emotion.upper()}**")
                
                # Mapping
                mapping = st.session_state.emotion_detector.map_emotion_to_params(emotion)
                st.session_state.mapping = mapping

    with col2:
        st.write("### 🎧 Step 2: Your Recommendations")
        
        if 'current_emotion' in st.session_state and st.session_state.spotify_client:
            if st.button("Get Fresh Tracks"):
                with st.spinner("Fetching music from Spotify..."):
                    tracks = st.session_state.spotify_client.get_recommendations(
                        st.session_state.mapping
                    )
                    st.session_state.recommended_tracks = tracks

            if 'recommended_tracks' in st.session_state:
                tracks = st.session_state.recommended_tracks
                
                if not tracks:
                    st.warning("No tracks found for this mood. Try again!")
                
                for track in tracks:
                    with st.container():
                        c1, c2 = st.columns([1, 3])
                        with c1:
                            st.image(track['album_art'], use_column_width=True)
                        with c2:
                            st.markdown(f"**{track['name']}**")
                            st.markdown(f"*{track['artist']}*")
                            st.markdown(f"[Listen on Spotify]({track['external_url']})")
                            if track['preview_url']:
                                st.audio(track['preview_url'], format="audio/mp3")
                        st.divider()
        else:
            st.info("Please take a photo first to get recommendations.")
            
    # Sidebar Info
    with st.sidebar:
        st.header("About MoodTune")
        st.write("""
            MoodTune uses Deep Learning (DeepFace) to recognize facial expressions 
            and maps them to Spotify's Audio Features:
            - **Valence**: Musical positiveness
            - **Energy**: Intensity and activity
        """)
        st.divider()
        st.caption("Powered by DeepFace & Spotify API")

if __name__ == "__main__":
    main()
