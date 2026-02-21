# Render endpoint - downloads from S3, renders, uploads result back to S3
# Copy and paste everything into backend/routes/render.py

import os
import threading
import tempfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from services.audio_analysis import analyze_audio
from services.matching_engine import build_edit_decision_list
from services.renderer import render_music_video
from services.s3_storage import download_file_from_s3, upload_file_to_s3, get_presigned_url
import boto3
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
job_status = {}

def list_s3_files(prefix: str) -> list:
    s3 = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    if "Contents" not in response:
        return []
    return [obj["Key"] for obj in response["Contents"]]


def run_render_job(project_id: str):
    try:
        job_status[project_id] = {"status": "processing", "message": "Downloading files..."}

        # Create temp workspace
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = os.path.join(tmp_dir, project_id)
            artist_dir = os.path.join(project_dir, "artist_clips")
            broll_dir = os.path.join(project_dir, "broll_clips")
            os.makedirs(artist_dir, exist_ok=True)
            os.makedirs(broll_dir, exist_ok=True)

            # Download song from S3
            song_files = list_s3_files(f"projects/{project_id}/song/")
            if not song_files:
                job_status[project_id] = {"status": "error", "message": "No song found"}
                return

            song_key = song_files[0]
            song_filename = song_key.split("/")[-1]
            song_local = os.path.join(project_dir, song_filename)
            download_file_from_s3(song_key, song_local)

            # Download artist clips from S3
            artist_keys = list_s3_files(f"projects/{project_id}/artist_clips/")
            for key in artist_keys:
                filename = key.split("/")[-1]
                download_file_from_s3(key, os.path.join(artist_dir, filename))

            # Download broll clips from S3
            broll_keys = list_s3_files(f"projects/{project_id}/broll_clips/")
            for key in broll_keys:
                filename = key.split("/")[-1]
                download_file_from_s3(key, os.path.join(broll_dir, filename))

            job_status[project_id] = {"status": "processing", "message": "Analyzing audio..."}
            audio_analysis = analyze_audio(song_local)

            job_status[project_id] = {"status": "processing", "message": "Matching clips..."}
            edit_decision_list = build_edit_decision_list(song_local, project_dir, audio_analysis)

            job_status[project_id] = {"status": "processing", "message": "Rendering video..."}
            output_dir = os.path.join(tmp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = render_music_video(edit_decision_list, output_dir)

            job_status[project_id] = {"status": "processing", "message": "Uploading to cloud..."}
            s3_output_key = f"projects/{project_id}/output/music_video.mp4"
            upload_file_to_s3(output_path, s3_output_key)

            job_status[project_id] = {"status": "done", "message": "Render complete"}

    except Exception as e:
        job_status[project_id] = {"status": "error", "message": str(e)}


@router.post("/render/{project_id}")
def start_render(project_id: str):
    job_status[project_id] = {"status": "queued", "message": "Starting..."}
    thread = threading.Thread(target=run_render_job, args=(project_id,))
    thread.daemon = True
    thread.start()
    return {"project_id": project_id, "status": "queued", "message": "Render started"}


@router.get("/status/{project_id}")
def get_status(project_id: str):
    if project_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status[project_id]


@router.get("/download/{project_id}")
def download_video(project_id: str):
    s3_key = f"projects/{project_id}/output/music_video.mp4"
    try:
        url = get_presigned_url(s3_key, expiry=3600)
        return RedirectResponse(url=url)
    except Exception:
        raise HTTPException(status_code=404, detail="Rendered video not found")