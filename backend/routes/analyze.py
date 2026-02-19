# This file defines the /api/analyze endpoint
# It analyzes both the song and all video clips in a project
# Copy and paste everything into backend/routes/analyze.py

import os
from fastapi import APIRouter, HTTPException
from services.audio_analysis import analyze_audio
from services.video_analysis import analyze_all_clips

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/analyze/{project_id}")
def analyze_project(project_id: str):
    # Find the project folder
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail="Project not found")

    # Find the song file
    song_file = None
    for file in os.listdir(project_dir):
        if file.lower().endswith((".mp3", ".wav")):
            song_file = os.path.join(project_dir, file)
            break

    if not song_file:
        raise HTTPException(status_code=404, detail="No song found in project")

    # Run audio analysis on the song
    audio_result = analyze_audio(song_file)

    # Run video analysis on all clips
    clip_results = analyze_all_clips(project_dir)

    return {
        "project_id": project_id,
        "audio_analysis": audio_result,
        "clip_analysis": clip_results
    }