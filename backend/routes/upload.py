import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(
    song: UploadFile = File(...),
    clips: List[UploadFile] = File(...)
):
    # Validate song file
    if not song.filename.endswith((".mp3", ".wav")):
        raise HTTPException(status_code=400, detail="Song must be an MP3 or WAV file")

    # Validate video clips
    for clip in clips:
        if not clip.filename.lower().endswith((".mp4", ".mov", ".avi")):
            raise HTTPException(status_code=400, detail=f"{clip.filename} is not a valid video file")

    # Create a unique project ID for this upload
    project_id = str(uuid.uuid4())
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)

    # Save the song
    song_path = os.path.join(project_dir, song.filename)
    with open(song_path, "wb") as f:
        f.write(await song.read())

    # Save each video clip
    saved_clips = []
    for clip in clips:
        clip_path = os.path.join(project_dir, clip.filename)
        with open(clip_path, "wb") as f:
            f.write(await clip.read())
        saved_clips.append(clip.filename)

    return {
        "project_id": project_id,
        "song": song.filename,
        "clips": saved_clips,
        "message": "Files uploaded successfully"
    }