from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.buckets import router as buckets_router
from src.api.auth.auth import get_current_user
from fastapi.responses import FileResponse
import os

# Check if we're in development mode
dev_mode = os.getenv('DEV_MODE', 'true').lower() == 'true'

app = FastAPI(
    title="CRONDA API", 
    description="Cloud Resource Deletion Automation API",
    version="0.1.0"
)

# Get the absolute path to the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Create directories if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the buckets router with conditional authentication
if dev_mode:
    app.include_router(buckets_router)  # No auth in dev mode
else:
    app.include_router(
        buckets_router,
        dependencies=[Depends(get_current_user)]
    )

templates = Jinja2Templates(directory=templates_dir)

@app.get("/health")
async def health_check():
    """Unprotected health check endpoint"""
    return {
        "status": "healthy",
        "mode": "development" if dev_mode else "production"
    }

@app.get("/")
async def root():
    """Unprotected root endpoint"""
    return {
        "message": "Welcome to CRONDA API",
        "mode": "development" if dev_mode else "production"
    }

@app.get("/ui")
async def ui(request: Request):
    """Protected UI endpoint"""
    return templates.TemplateResponse("index.html", {"request": request})