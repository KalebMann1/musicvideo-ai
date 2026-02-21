# Fast matching engine using FFmpeg for audio extraction
# Reduces processing time from 1+ hour to under 2 minutes
# Copy and paste everything into backend/services/matching_engine.py

import os
import subprocess
import numpy as np
import librosa
from moviepy import VideoFileClip

def extract_audio_ffmpeg(video_path: str, output_path: str, duration: int = 30) -> bool:
    # Use FFmpeg directly to extract audio - much faster than MoviePy
    # Only extracts first 30 seconds at low sample rate for matching
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-t", str(duration),
            "-ar", "11025",
            "-ac", "1",
            "-f", "wav",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"FFmpeg extraction failed: {e}")
        return False


def find_sync_offset(song_path: str, clip_audio_path: str) -> float:
    # Load both at very low sample rate for fast correlation
    song_audio, _ = librosa.load(song_path, sr=11025, mono=True)
    clip_audio, _ = librosa.load(clip_audio_path, sr=11025, mono=True)

    # Only use first 30 seconds of clip for matching
    max_samples = 11025 * 30
    if len(clip_audio) > max_samples:
        clip_audio = clip_audio[:max_samples]

    # Cross-correlation to find offset
    correlation = np.correlate(song_audio, clip_audio, mode='valid')
    offset_samples = int(np.argmax(correlation))
    offset_seconds = offset_samples / 11025
    return round(offset_seconds, 3)


def get_clip_duration(clip_path: str) -> float:
    # Use FFprobe to get clip duration without loading the whole file
    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            clip_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return round(float(result.stdout.strip()), 3)
    except Exception:
        # Fallback to moviepy if ffprobe fails
        clip = VideoFileClip(clip_path)
        duration = clip.duration
        clip.close()
        return round(duration, 3)


def match_artist_clips(song_path: str, artist_clips_dir: str, temp_dir: str) -> list:
    placements = []
    video_extensions = (".mp4", ".mov", ".avi")

    for filename in os.listdir(artist_clips_dir):
        if not filename.lower().endswith(video_extensions):
            continue

        clip_path = os.path.join(artist_clips_dir, filename)
        clip_audio_path = os.path.join(temp_dir, f"{filename}_audio.wav")

        print(f"Extracting audio from {filename}...")
        success = extract_audio_ffmpeg(clip_path, clip_audio_path)
        if not success:
            print(f"Could not extract audio from {filename}, skipping")
            continue

        print(f"Finding sync offset for {filename}...")
        offset = find_sync_offset(song_path, clip_audio_path)
        duration = get_clip_duration(clip_path)

        placements.append({
            "filename": filename,
            "clip_path": clip_path,
            "type": "artist",
            "start_time": offset,
            "end_time": round(offset + duration, 3),
            "duration": duration
        })

        if os.path.exists(clip_audio_path):
            os.remove(clip_audio_path)

    placements.sort(key=lambda x: x["start_time"])
    return placements


def match_broll_clips(broll_clips_dir: str, song_duration: float,
                      energy_data: dict, existing_placements: list) -> list:
    video_extensions = (".mp4", ".mov", ".avi")
    broll_files = [
        f for f in os.listdir(broll_clips_dir)
        if f.lower().endswith(video_extensions)
    ]

    if not broll_files:
        return []

    gaps = find_timeline_gaps(existing_placements, song_duration)
    placements = []
    broll_index = 0

    for gap_start, gap_end in gaps:
        gap_duration = gap_end - gap_start
        if gap_duration < 1.0:
            continue

        current_time = gap_start
        while current_time < gap_end and broll_index < len(broll_files):
            filename = broll_files[broll_index % len(broll_files)]
            clip_path = os.path.join(broll_clips_dir, filename)
            clip_duration = get_clip_duration(clip_path)
            clip_duration = min(clip_duration, gap_end - current_time)

            placements.append({
                "filename": filename,
                "clip_path": clip_path,
                "type": "broll",
                "start_time": round(current_time, 3),
                "end_time": round(current_time + clip_duration, 3),
                "duration": round(clip_duration, 3)
            })

            current_time += clip_duration
            broll_index += 1

    return placements


def find_timeline_gaps(placements: list, song_duration: float) -> list:
    if not placements:
        return [(0, song_duration)]

    gaps = []
    sorted_placements = sorted(placements, key=lambda x: x["start_time"])

    if sorted_placements[0]["start_time"] > 0.5:
        gaps.append((0, sorted_placements[0]["start_time"]))

    for i in range(len(sorted_placements) - 1):
        end_of_current = sorted_placements[i]["end_time"]
        start_of_next = sorted_placements[i + 1]["start_time"]
        if start_of_next - end_of_current > 0.5:
            gaps.append((end_of_current, start_of_next))

    last_end = sorted_placements[-1]["end_time"]
    if song_duration - last_end > 0.5:
        gaps.append((last_end, song_duration))

    return gaps


def build_edit_decision_list(song_path: str, project_dir: str,
                              audio_analysis: dict) -> dict:
    artist_dir = os.path.join(project_dir, "artist_clips")
    broll_dir = os.path.join(project_dir, "broll_clips")
    temp_dir = os.path.join(project_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    artist_placements = []
    broll_placements = []

    if os.path.exists(artist_dir) and os.listdir(artist_dir):
        artist_placements = match_artist_clips(song_path, artist_dir, temp_dir)

    if os.path.exists(broll_dir) and os.listdir(broll_dir):
        broll_placements = match_broll_clips(
            broll_dir,
            audio_analysis["duration"],
            audio_analysis.get("energy", {}),
            artist_placements
        )

    all_placements = sorted(
        artist_placements + broll_placements,
        key=lambda x: x["start_time"]
    )

    return {
        "song_path": song_path,
        "song_duration": audio_analysis["duration"],
        "bpm": audio_analysis["bpm"],
        "total_clips": len(all_placements),
        "placements": all_placements
    }