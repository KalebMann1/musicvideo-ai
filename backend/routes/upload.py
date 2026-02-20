# Updated upload endpoint that handles two clip types:
# artist_clips (lip sync clips that need audio matching)
# broll_clips (filler clips that get placed by energy matching)
# Copy and paste everything into backend/routes/upload.py

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def is_valid_video(filename: str) -> bool:
    return filename.lower().endswith((".mp4", ".mov", ".avi"))

def is_valid_audio(filename: str) -> bool:
    return filename.lower().endswith((".mp3", ".wav"))

@router.post("/upload")
async def upload_files(
    song: UploadFile = File(...),
    artist_clips: List[UploadFile] = File(default=[]),
        broll_clips: List[UploadFile] = File(default=[])
):
    # Validate song
    if not is_valid_audio(song.filename):
        raise HTTPException(status_code=400, detail="Song must be an MP3 or WAV file")

    # Make sure at least one clip type was uploaded
    if not artist_clips and not broll_clips:
        raise HTTPException(status_code=400, detail="Upload at least one artist clip or B-roll clip")

    # Validate artist clips if provided
    if artist_clips:
        for clip in artist_clips:
            if not is_valid_video(clip.filename):
                raise HTTPException(status_code=400, detail=f"{clip.filename} is not a valid video file")

    # Validate broll clips if provided
    if broll_clips:
        for clip in broll_clips:
            if not is_valid_video(clip.filename):
                raise HTTPException(status_code=400, detail=f"{clip.filename} is not a valid video file")

    # Create project folder structure
    project_id = str(uuid.uuid4())
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    artist_dir = os.path.join(project_dir, "artist_clips")
    broll_dir = os.path.join(project_dir, "broll_clips")

    os.makedirs(artist_dir, exist_ok=True)
    os.makedirs(broll_dir, exist_ok=True)

    # Save the song
    song_path = os.path.join(project_dir, song.filename)
    with open(song_path, "wb") as f:
        f.write(await song.read())

    # Save artist clips
    saved_artist_clips = []
    if artist_clips:
        for clip in artist_clips:
            clip_path = os.path.join(artist_dir, clip.filename)
            with open(clip_path, "wb") as f:
                f.write(await clip.read())
            saved_artist_clips.append(clip.filename)

    # Save broll clips
    saved_broll_clips = []
    if broll_clips:
        for clip in broll_clips:
            clip_path = os.path.join(broll_dir, clip.filename)
            with open(clip_path, "wb") as f:
                f.write(await clip.read())
            saved_broll_clips.append(clip.filename)

    return {
        "project_id": project_id,
        "song": song.filename,
        "artist_clips": saved_artist_clips,
        "broll_clips": saved_broll_clips,
        "message": "Files uploaded successfully"
    }