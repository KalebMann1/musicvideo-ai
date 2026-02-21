# Async render endpoint - starts rendering in background and returns immediately
# Frontend polls /api/status/{project_id} to check when it's done
# Copy and paste everything into backend/routes/render.py

import os
import json
import threading
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.audio_analysis import analyze_audio
from services.matching_engine import build_edit_decision_list
from services.renderer import render_music_video

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

# In-memory job status tracker
job_status = {}

def run_render_job(project_id: str, song_file: str, project_dir: str):
    # This runs in a background thread
    try:
        job_status[project_id] = {"status": "processing", "message": "Analyzing audio..."}

        audio_analysis = analyze_audio(song_file)

        job_status[project_id] = {"status": "processing", "message": "Matching clips..."}

        edit_decision_list = build_edit_decision_list(song_file, project_dir, audio_analysis)

        job_status[project_id] = {"status": "processing", "message": "Rendering video..."}

        output_dir = os.path.join(OUTPUT_DIR, project_id)
        render_music_video(edit_decision_list, output_dir)

        job_status[project_id] = {"status": "done", "message": "Render complete"}

    except Exception as e:
        job_status[project_id] = {"status": "error", "message": str(e)}


@router.post("/render/{project_id}")
def start_render(project_id: str):
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

    # Start rendering in a background thread
    job_status[project_id] = {"status": "queued", "message": "Starting..."}
    thread = threading.Thread(target=run_render_job, args=(project_id, song_file, project_dir))
    thread.daemon = True
    thread.start()

    return {"project_id": project_id, "status": "queued", "message": "Render started"}


@router.get("/status/{project_id}")
def get_status(project_id: str):
    if project_id not in job_status:
        # Check if output already exists from a previous render
        output_path = os.path.join(OUTPUT_DIR, project_id, "music_video.mp4")
        if os.path.exists(output_path):
            return {"status": "done", "message": "Render complete"}
        raise HTTPException(status_code=404, detail="Job not found")

    return job_status[project_id]


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