# This endpoint triggers the video renderer
# It takes a project_id, runs the full pipeline, and returns a download link
# Copy and paste everything into backend/routes/render.py

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.audio_analysis import analyze_audio
from services.matching_engine import build_edit_decision_list
from services.renderer import render_music_video

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

@router.post("/render/{project_id}")
def render_project(project_id: str):
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

    # Run the full pipeline
    audio_analysis = analyze_audio(song_file)
    edit_decision_list = build_edit_decision_list(song_file, project_dir, audio_analysis)

    # Render the video
    output_dir = os.path.join(OUTPUT_DIR, project_id)
    output_path = render_music_video(edit_decision_list, output_dir)

    return {
        "project_id": project_id,
        "output_path": output_path,
        "message": "Music video rendered successfully",
        "download_url": f"/api/download/{project_id}"
    }


@router.get("/download/{project_id}")
def download_video(project_id: str):
    output_path = os.path.join(OUTPUT_DIR, project_id, "music_video.mp4")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Rendered video not found")

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="music_video.mp4"
    )