# This service analyzes a song and extracts useful information
# like BPM, energy levels, and song sections
# Copy and paste everything into backend/services/audio_analysis.py

import librosa
import numpy as np

def analyze_audio(file_path: str) -> dict:
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)

    # Get the BPM (tempo) of the song
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    # Get the total duration of the song in seconds
    duration = librosa.get_duration(y=y, sr=sr)

    # Calculate the energy of the song over time
    # This tells us which parts of the song are loud/intense vs calm
    rms = librosa.feature.rms(y=y)[0]
    energy_times = librosa.frames_to_time(range(len(rms)), sr=sr).tolist()
    energy_values = rms.tolist()

    # Detect the overall mood using spectral features
    # Higher spectral centroid = brighter/more energetic sound
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    avg_brightness = float(np.mean(spectral_centroid))

    # Divide the song into sections based on structure
    # This helps us know where the intro, verse, chorus etc roughly are
    segment_boundaries = librosa.segment.agglomerative(
        librosa.feature.mfcc(y=y, sr=sr), 8
    )
    segment_times = librosa.frames_to_time(segment_boundaries, sr=sr).tolist()

    return {
        "duration": round(duration, 2),
        "bpm": round(float(np.asarray(tempo).flat[0]), 2),
        "beat_times": beat_times,
        "energy": {
            "times": energy_times,
            "values": energy_values
        },
        "avg_brightness": round(avg_brightness, 2),
        "segments": segment_times
    }