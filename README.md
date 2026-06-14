# MoodTune: Emotion-Based Music Recommender

MoodTune is a full-stack application that uses Computer Vision to detect your current emotion via your webcam and recommends a personalized Spotify playlist that matches your mood.

## Features
- **Facial Emotion Detection**: Uses the DeepFace library to analyze expressions (Happy, Sad, Angry, etc.).
- **Spotify Integration**: Leverages the Spotify Web API to fetch tracks based on audio features like valence (musical happiness) and energy.
- **Interactive UI**: Built with Streamlit for a seamless camera-to-music experience.
- **Audio Previews**: Listen to 30-second snippets of recommended tracks directly in the app.

## Prerequisites
- Python 3.9 or higher
- A Spotify Developer account

## Installation

1.  **Clone the project files** to your local machine.

2.  **Install dependencies**:
    bash
    pip install -r requirements.txt
    

3.  **Setup Spotify API Credentials**:
    - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
    - Create a new App.
    - Copy your `Client ID` and `Client Secret`.
    - Create a file named `.env` in the root directory (or rename `.env.example`).
    - Add your credentials:
      text
      SPOTIPY_CLIENT_ID=your_id_here
      SPOTIPY_CLIENT_SECRET=your_secret_here
      

## Running the Application

Start the Streamlit server:
bash
streamlit run app.py


## How it Works
1.  **Camera Input**: Streamlit's `st.camera_input` captures a snapshot of your face.
2.  **Processing**: `DeepFace` analyzes the image to determine the dominant emotion.
3.  **Mapping**: The emotion is mapped to specific Spotify parameters:
    - **Happy**: High Valence, High Energy
    - **Sad**: Low Valence, Low Energy
    - **Angry**: High Energy, Low Valence
4.  **Recommendation**: `Spotipy` calls the `recommendations` endpoint using these parameters and a set of relevant seed genres.

## Troubleshooting
- **Model Download**: On the first run, DeepFace will download the pre-trained weights (approx. 100-200MB). Ensure you have a stable internet connection.
- **No Face Detected**: If the app fails to detect a face, it defaults to a 'neutral' mood. Ensure your face is well-lit and centered.
- **Spotify API Errors**: Ensure your Client ID and Secret are correct and your internet connection is active.
