# Fixed renderer that respects start_time offsets and preserves original resolution
# Copy and paste everything into backend/services/renderer.py

import os
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, ColorClip

def render_music_video(edit_decision_list: dict, output_dir: str) -> str:
    song_path = edit_decision_list["song_path"]
    song_duration = edit_decision_list["song_duration"]
    placements = edit_decision_list["placements"]

    if not placements:
        raise ValueError("No clips to render")

    os.makedirs(output_dir, exist_ok=True)

    # Get resolution from the first clip so we preserve the original
    first_clip = VideoFileClip(placements[0]["clip_path"])
    video_size = first_clip.size
    fps = first_clip.fps or 30
    first_clip.close()

    # Build the full timeline including black screens for gaps
    timeline_clips = []
    current_time = 0.0

    for placement in placements:
        start_time = placement["start_time"]
        duration = placement["duration"]
        clip_path = placement["clip_path"]

        # If there's a gap before this clip, fill it with a black screen
        gap = start_time - current_time
        if gap > 0.05:
            black = ColorClip(size=video_size, color=[0, 0, 0], duration=gap)
            black = black.with_fps(fps)
            timeline_clips.append(black)

        # Load and trim the clip to its intended duration
        clip = VideoFileClip(clip_path)
        clip = clip.subclipped(0, min(duration, clip.duration))

        # Resize to match the first clip's resolution if different
        if clip.size != video_size:
            clip = clip.resized(video_size)

        timeline_clips.append(clip)
        current_time = start_time + duration

    # Fill any remaining time at the end with black
    remaining = song_duration - current_time
    if remaining > 0.05:
        black = ColorClip(size=video_size, color=[0, 0, 0], duration=remaining)
        black = black.with_fps(fps)
        timeline_clips.append(black)

    # Concatenate everything
    final_video = concatenate_videoclips(timeline_clips, method="compose")

    # Add the song as the audio track
    song_audio = AudioFileClip(song_path)
    if song_audio.duration > final_video.duration:
        song_audio = song_audio.subclipped(0, final_video.duration)

    final_video = final_video.with_audio(song_audio)

    # Export the final video
    output_path = os.path.join(output_dir, "music_video.mp4")
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        logger=None
    )

    # Clean up
    for clip in timeline_clips:
        clip.close()
    song_audio.close()
    final_video.close()

    return output_path