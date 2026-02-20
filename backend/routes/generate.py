# This endpoint triggers the matching engine and builds the edit decision list
# Copy and paste everything into backend/routes/generate.py

import os
from fastapi import APIRouter, HTTPException
from services.audio_analysis import analyze_audio
from services.matching_engine import build_edit_decision_list

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/generate/{project_id}")
def generate_edit(project_id: str):
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail="Project not found")

    # Find the song
    song_file = None
    for file in os.listdir(project_dir):
        if file.lower().endswith((".mp3", ".wav")):
            song_file = os.path.join(project_dir, file)
            break

    if not song_file:
        raise HTTPException(status_code=404, detail="No song found in project")

    # Analyze the audio first
    audio_analysis = analyze_audio(song_file)

    # Build the edit decision list
    edit_decision_list = build_edit_decision_list(
        song_file,
        project_dir,
        audio_analysis
    )

    return {
        "project_id": project_id,
        "edit_decision_list": edit_decision_list
    }