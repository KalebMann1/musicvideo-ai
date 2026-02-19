from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MusicVideo AI", version="1.0.0")

# This allows our frontend to talk to our backend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MusicVideo AI backend is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}