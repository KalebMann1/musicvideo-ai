# This service analyzes each video clip to understand its characteristics
# It looks at motion, brightness, and color to help match clips to song sections
# Copy and paste everything into backend/services/video_analysis.py

import cv2
import numpy as np
import os

def analyze_clip(file_path: str) -> dict:
    # Open the video file
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        return {"error": f"Could not open video file: {file_path}"}

    # Get basic video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    brightness_values = []
    motion_values = []
    prev_gray = None

    # Sample every 10th frame so analysis runs fast
    sample_interval = 10
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_interval == 0:
            # Calculate brightness of this frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = float(np.mean(gray))
            brightness_values.append(brightness)

            # Calculate motion by comparing this frame to the previous one
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                motion = float(np.mean(diff))
                motion_values.append(motion)

            prev_gray = gray

        frame_idx += 1

    cap.release()

    # Summarize the results
    avg_brightness = round(float(np.mean(brightness_values)), 2) if brightness_values else 0
    avg_motion = round(float(np.mean(motion_values)), 2) if motion_values else 0
    max_motion = round(float(np.max(motion_values)), 2) if motion_values else 0

    # Classify the clip energy as low, medium, or high
    if avg_motion < 3:
        energy_level = "low"
    elif avg_motion < 8:
        energy_level = "medium"
    else:
        energy_level = "high"

    return {
        "filename": os.path.basename(file_path),
        "duration": round(duration, 2),
        "resolution": f"{width}x{height}",
        "fps": round(fps, 2),
        "avg_brightness": avg_brightness,
        "avg_motion": avg_motion,
        "max_motion": max_motion,
        "energy_level": energy_level
    }


def analyze_all_clips(project_dir: str) -> list:
    # Find all video files in the project folder and analyze each one
    results = []
    video_extensions = (".mp4", ".mov", ".avi")

    for file in os.listdir(project_dir):
        if file.lower().endswith(video_extensions):
            file_path = os.path.join(project_dir, file)
            clip_data = analyze_clip(file_path)
            results.append(clip_data)

    return results