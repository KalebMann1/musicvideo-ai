# Main entry point for the backend server
# Copy and paste everything into backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router
from routes.analyze import router as analyze_router
from routes.generate import router as generate_router
from routes.render import router as render_router

app = FastAPI(title="MusicVideo AI", version="1.0.0")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(upload_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(generate_router, prefix="/api")
app.include_router(render_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "MusicVideo AI backend is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}