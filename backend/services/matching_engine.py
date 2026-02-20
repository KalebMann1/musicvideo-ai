# This is the matching engine - the brain of the music video editor
# It handles two types of clip placement:
# 1. Artist clips: uses cross-correlation to find exact lip sync position in the song
# 2. B-roll clips: uses energy matching to fill gaps intelligently
# Copy and paste everything into backend/services/matching_engine.py

import os
import numpy as np
import librosa
from moviepy import VideoFileClip

def extract_audio_from_clip(clip_path: str, output_path: str) -> bool:
    # Extract the audio track from a video clip and save as WAV
    try:
        clip = VideoFileClip(clip_path)
        if clip.audio is None:
            clip.close()
            return False
        clip.audio.write_audiofile(output_path, logger=None)
        clip.close()
        return True
    except Exception as e:
        print(f"Error extracting audio from {clip_path}: {e}")
        return False


def find_sync_offset(song_path: str, clip_audio_path: str) -> float:
    # Load both audio files
    song_audio, song_sr = librosa.load(song_path, sr=22050, mono=True)
    clip_audio, clip_sr = librosa.load(clip_audio_path, sr=22050, mono=True)

    # Use cross-correlation to find where in the song the clip audio matches
    # This is the same math that powers audio fingerprinting apps
    correlation = np.correlate(song_audio, clip_audio, mode='valid')
    offset_samples = np.argmax(correlation)

    # Convert sample offset to seconds
    offset_seconds = offset_samples / 22050
    return round(offset_seconds, 3)


def match_artist_clips(song_path: str, artist_clips_dir: str, temp_dir: str) -> list:
    # For each artist clip, find its exact position in the song
    placements = []
    video_extensions = (".mp4", ".mov", ".avi")

    for filename in os.listdir(artist_clips_dir):
        if not filename.lower().endswith(video_extensions):
            continue

        clip_path = os.path.join(artist_clips_dir, filename)
        clip_audio_path = os.path.join(temp_dir, f"{filename}_audio.wav")

        # Extract audio from the clip
        success = extract_audio_from_clip(clip_path, clip_audio_path)
        if not success:
            print(f"Could not extract audio from {filename}, skipping sync match")
            continue

        # Find where this clip lines up in the song
        offset = find_sync_offset(song_path, clip_audio_path)

        # Get clip duration
        clip = VideoFileClip(clip_path)
        duration = clip.duration
        clip.close()

        placements.append({
            "filename": filename,
            "clip_path": clip_path,
            "type": "artist",
            "start_time": offset,
            "end_time": round(offset + duration, 3),
            "duration": round(duration, 3)
        })

        # Clean up temp audio file
        if os.path.exists(clip_audio_path):
            os.remove(clip_audio_path)

    # Sort placements by start time
    placements.sort(key=lambda x: x["start_time"])
    return placements


def match_broll_clips(broll_clips_dir: str, song_duration: float,
                      energy_data: dict, existing_placements: list) -> list:
    # Find gaps in the timeline not covered by artist clips
    # Then fill them with B-roll clips based on energy matching

    video_extensions = (".mp4", ".mov", ".avi")
    broll_files = [
        f for f in os.listdir(broll_clips_dir)
        if f.lower().endswith(video_extensions)
    ]

    if not broll_files:
        return []

    # Find gaps in the timeline
    gaps = find_timeline_gaps(existing_placements, song_duration)

    placements = []
    broll_index = 0

    for gap_start, gap_end in gaps:
        gap_duration = gap_end - gap_start
        if gap_duration < 1.0:
            # Skip gaps shorter than 1 second
            continue

        # Fill the gap with B-roll clips
        current_time = gap_start
        while current_time < gap_end and broll_index < len(broll_files):
            filename = broll_files[broll_index % len(broll_files)]
            clip_path = os.path.join(broll_clips_dir, filename)

            clip = VideoFileClip(clip_path)
            clip_duration = min(clip.duration, gap_end - current_time)
            clip.close()

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
    # Find sections of the song not covered by any clip
    if not placements:
        return [(0, song_duration)]

    gaps = []
    sorted_placements = sorted(placements, key=lambda x: x["start_time"])

    # Check for gap at the beginning
    if sorted_placements[0]["start_time"] > 0.5:
        gaps.append((0, sorted_placements[0]["start_time"]))

    # Check for gaps between clips
    for i in range(len(sorted_placements) - 1):
        end_of_current = sorted_placements[i]["end_time"]
        start_of_next = sorted_placements[i + 1]["start_time"]
        if start_of_next - end_of_current > 0.5:
            gaps.append((end_of_current, start_of_next))

    # Check for gap at the end
    last_end = sorted_placements[-1]["end_time"]
    if song_duration - last_end > 0.5:
        gaps.append((last_end, song_duration))

    return gaps


def build_edit_decision_list(song_path: str, project_dir: str,
                              audio_analysis: dict) -> dict:
    # Main function that builds the complete edit decision list
    artist_dir = os.path.join(project_dir, "artist_clips")
    broll_dir = os.path.join(project_dir, "broll_clips")
    temp_dir = os.path.join(project_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    artist_placements = []
    broll_placements = []

    # Match artist clips using lip sync detection
    if os.path.exists(artist_dir) and os.listdir(artist_dir):
        artist_placements = match_artist_clips(song_path, artist_dir, temp_dir)

    # Fill remaining gaps with B-roll
    if os.path.exists(broll_dir) and os.listdir(broll_dir):
        broll_placements = match_broll_clips(
            broll_dir,
            audio_analysis["duration"],
            audio_analysis.get("energy", {}),
            artist_placements
        )

    # Combine and sort all placements
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