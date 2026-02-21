# Upload endpoint - saves files to AWS S3 instead of local disk
# Copy and paste everything into backend/routes/upload.py

import os
import uuid
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from services.s3_storage import upload_fileobj_to_s3

router = APIRouter()

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
    if not is_valid_audio(song.filename):
        raise HTTPException(status_code=400, detail="Song must be an MP3 or WAV file")

    if not artist_clips and not broll_clips:
        raise HTTPException(status_code=400, detail="Upload at least one clip")

    if artist_clips:
        for clip in artist_clips:
            if not is_valid_video(clip.filename):
                raise HTTPException(status_code=400, detail=f"{clip.filename} is not a valid video file")

    if broll_clips:
        for clip in broll_clips:
            if not is_valid_video(clip.filename):
                raise HTTPException(status_code=400, detail=f"{clip.filename} is not a valid video file")

    project_id = str(uuid.uuid4())

    # Upload song to S3
    song_key = f"projects/{project_id}/song/{song.filename}"
    upload_fileobj_to_s3(song.file, song_key)

    # Upload artist clips to S3
    saved_artist_clips = []
    for clip in artist_clips:
        key = f"projects/{project_id}/artist_clips/{clip.filename}"
        upload_fileobj_to_s3(clip.file, key)
        saved_artist_clips.append(clip.filename)

    # Upload broll clips to S3
    saved_broll_clips = []
    for clip in broll_clips:
        key = f"projects/{project_id}/broll_clips/{clip.filename}"
        upload_fileobj_to_s3(clip.file, key)
        saved_broll_clips.append(clip.filename)

    return {
        "project_id": project_id,
        "song": song.filename,
        "artist_clips": saved_artist_clips,
        "broll_clips": saved_broll_clips,
        "message": "Files uploaded successfully"
    }