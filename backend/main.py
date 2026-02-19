# This is the main entry point for the backend server
# Copy and paste everything in this block into backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router

app = FastAPI(title="MusicVideo AI", version="1.0.0")

# This allows our frontend to talk to our backend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the upload routes under /api
app.include_router(upload_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "MusicVideo AI backend is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}