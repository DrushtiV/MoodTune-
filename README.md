# MoodTune 🎵 - Emotion-Based Music Recommender

MoodTune captures your facial expression via webcam, detects your current 
emotion using deep learning, and recommends a personalised Spotify playlist 
that matches your mood — all in real time.

---

## Features

- **Facial Emotion Detection** — DeepFace (VGG-Face CNN) classifies 7 emotions:
  happy, sad, angry, surprise, neutral, fear, disgust.
- **Spotify Integration** — Spotipy calls the Spotify Recommendations API with 
  audio feature targets (valence, energy) and seed genres.
- **30-Second Audio Previews** — Listen to snippet previews inside the app 
  without leaving the browser.
- **Graceful Fallback** — If no face is detected, the app defaults to neutral 
  mood and still returns valid recommendations.
- **Session Caching** — Models and API clients are initialised once per session 
  via `st.session_state`, avoiding repeated cold starts.

---

## Project Structure
moodtune/

 ├── app.py # Streamlit UI, session state, main layout

 ├── emotion_processor.py # DeepFace wrapper + emotion→params mapping
 
 ├── spotify_client.py # Spotipy wrapper for Recommendations API
 
 ├── requirements.txt
 
 ├── .env.example # Credentials template
 
 └── README.md

---

## Prerequisites

- Python 3.9 or higher
- A Spotify Developer account (free)
- Webcam access in the browser

---

## Installation

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

On first run, DeepFace will automatically download the pre-trained VGG-Face 
emotion weights (~100–200 MB). Ensure a stable internet connection.

**2. Set up Spotify API credentials**

Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard), 
create an App, and copy your Client ID and Client Secret.

```bash
cp .env.example .env
```

Edit `.env`:
SPOTIPY_CLIENT_ID=your_client_id_here
 SPOTIPY_CLIENT_SECRET=your_client_secret_here

**3. Run the app**
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## How It Works

### Step 1 — Webcam Capture
Streamlit's `st.camera_input` widget opens the device camera. On capture, 
it returns a JPEG byte stream that is decoded into a PIL Image and then 
converted to a NumPy RGB array for processing.

### Step 2 — Facial Emotion Recognition
The RGB array is passed to `EmotionDetector.analyze_emotion()`:

1. **Colour space conversion** — RGB → BGR via `cv2.cvtColor`, matching 
   OpenCV's native format.
2. **Face detection** — OpenCV's Haar cascade detects the face region 
   (detector_backend='opencv'). With `enforce_detection=False`, the full 
   frame is analysed even if no clear face is found.
3. **Emotion classification** — DeepFace runs the VGG-Face CNN to produce 
   a probability distribution across 7 emotion classes. The 
   `dominant_emotion` (argmax) is returned.

### Step 3 — Emotion → Audio Feature Mapping
`map_emotion_to_params()` converts the emotion string into Spotify audio 
feature targets via a lookup table:

| Emotion  | Valence | Energy | Seed Genres               |
|----------|---------|--------|---------------------------|
| happy    | 0.8     | 0.8    | happy, pop, dance         |
| sad      | 0.2     | 0.2    | acoustic, piano, sad      |
| angry    | 0.1     | 0.9    | rock, metal, hardcore     |
| surprise | 0.7     | 0.8    | electronic, party, indie-pop |
| neutral  | 0.5     | 0.5    | ambient, chill, acoustic  |
| fear     | 0.2     | 0.6    | ambient, soundtrack, classical |
| disgust  | 0.3     | 0.4    | grunge, blues, alternative |

### Step 4 — Spotify Recommendations API Call
`SpotifyRecommender.get_recommendations()` calls the Spotify Web API:

```python
sp.recommendations(
    seed_genres=['happy', 'pop', 'dance'],
    target_valence=0.8,
    target_energy=0.8,
    limit=10
)
```

The Client Credentials OAuth flow is used — no user login required. The 
returned track objects are parsed for name, artist, album art URL, 
external Spotify URL, and 30-second preview URL.

### Step 5 — UI Rendering
Results are displayed as track cards: album art thumbnail, track name, 
artist name, a link to Spotify, and an inline `st.audio` widget for 
the preview clip.

---

## Technical Architecture
<img width="1408" height="768" alt="Gemini_Generated_Image_5npiv15npiv15npi" src="https://github.com/user-attachments/assets/2cd4a35c-0477-4a3f-8a1e-630af8ccf80c" />

---

## Key Technical Concepts

### DeepFace and the VGG-Face CNN
DeepFace is a lightweight Python wrapper around several state-of-the-art 
face analysis models. For emotion detection it uses a CNN trained on the 
FER-2013 dataset (35,887 labelled facial images across 7 classes). The 
model architecture is a VGG-style convolutional network with:
- Multiple Conv2D + MaxPooling blocks for spatial feature extraction
- Fully connected layers for classification
- Softmax output over 7 emotion classes

`DeepFace.build_model("Emotion")` is called at `__init__` time to 
pre-warm the model and avoid latency on the first prediction.

### Spotify Audio Features — Valence and Energy
The Recommendations API accepts continuous audio feature targets in [0.0, 1.0]:

- **Valence** — Measures musical "positiveness". High valence = happy, 
  cheerful, euphoric. Low valence = sad, depressed, angry.
- **Energy** — Perceptual intensity and activity. High energy = fast, 
  loud, noisy (e.g. metal). Low energy = slow, quiet, calm (e.g. piano ballad).

These two axes create a 2D mood space that maps naturally onto the 
arousal-valence circumplex model from affective psychology.

### Spotify Client Credentials OAuth Flow
The app uses `SpotifyClientCredentials` — a server-side OAuth 2.0 flow 
that authenticates the application itself (not a user). This grants 
access to public catalogue endpoints like `/recommendations` without 
requiring the user to log in to Spotify. The `client_id` and 
`client_secret` are loaded from environment variables via `python-dotenv`.

### Session State Architecture
Streamlit reruns the entire script on every interaction. To avoid 
re-initialising the DeepFace model (expensive: model download + load) 
and Spotify client on each button click, both are stored in 
`st.session_state` on first load and reused across reruns.

---

## Emotion Mapping Design Rationale

The valence/energy mapping follows the **Russell Circumplex Model of Affect** — 
a widely used psychological framework that maps all human emotions onto a 
2D plane of valence (pleasure) and arousal (energy):
High Energy
 │ Angry Surprised / Happy
 │
 ─────┼───────────────────────────── Valence
 │
 │ Fear / Disgust Sad / Neutral
 Low Energy

Spotify's valence and energy features map almost directly onto this 
plane, making it a natural bridge between facial affect recognition 
and music retrieval.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| First run is slow | DeepFace is downloading pre-trained weights (~150 MB). Wait for completion. |
| "No face detected" | Ensure face is well-lit and centred. App falls back to neutral mood. |
| Spotify credentials error | Verify `.env` has correct Client ID/Secret with no extra spaces. |
| Camera not available | Allow browser camera permissions. On some systems use `http://` not `https://`. |
| `ModuleNotFoundError: tf-keras` | Run `pip install tf-keras tensorflow` — required for DeepFace with TF 2.16+. |
| No preview audio plays | ~30% of Spotify tracks have no preview URL. These are silently skipped. |

---

## Requirements
streamlit==1.32.0
 deepface==0.0.82
 opencv-python-headless==4.9.0.80
 spotipy==2.23.0
 python-dotenv==1.0.1
 Pillow==10.2.0
 tf-keras==2.16.0
 tensorflow==2.16.1

Python 3.9–3.11 recommended. TensorFlow 2.16 requires `tf-keras` as a 
separate package (it was decoupled from the main TF release).

---

## Limitations

- **Single face only** — Only the first detected face is analysed. 
  Group photos use the first result.
- **Static image** — Emotion is detected from a single snapshot, not 
  a video stream. A momentary expression may not reflect sustained mood.
- **Genre constraints** — Spotify's seed genre list is limited; 
  not all genre strings are valid API seeds.
- **Preview availability** — Spotify preview URLs are not available 
  for all tracks (~30% missing) depending on region and licensing.
- **No user auth** — Client Credentials flow cannot access user 
  playlists, playback control, or personalised history.


--------------------------------------------
