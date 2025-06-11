from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import create_db_and_tables

from routes import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database initialized!")
    yield
    # Shutdown logic
    print("Shutting down...")


app = FastAPI(
    title="Clara",
    description="Backend for Clara, your intelligent personal assistant",
    version="0.1.0",
    lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to Clara's API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "OK", "service": "Clara Backend"}


app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    print("Starting Clara's backend server...")
    print("Server will be available at: http://localhost:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
