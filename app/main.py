from fastapi import FastAPI, WebSocket, UploadFile, Form, BackgroundTasks, HTTPException, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import uuid
from datetime import datetime
from app.services.translation import translate_text
from app.services.database import save_file_history, get_file_history
from app.utils.websocket import WebSocketManager

app = FastAPI()

# Set up directories and templates
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
TEMPLATES = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# WebSocket manager
websocket_manager = WebSocketManager()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Render the main upload page."""
    return TEMPLATES.TemplateResponse("index.html", {"request": {}})

@app.post("/upload/")
async def upload_file(file: UploadFile, language: str = Form(...), background_tasks: BackgroundTasks = None):
    """Handle file uploads and start translation."""
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed.")

    session_id = str(uuid.uuid4())
    input_file = UPLOAD_DIR / f"{session_id}_{file.filename}"

    with input_file.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Notify WebSocket and start translation in the background
    await websocket_manager.broadcast(f"File uploaded: {file.filename}. Starting translation.")
    background_tasks.add_task(process_translation, session_id, input_file, language)

    return {"message": "File uploaded successfully.", "session_id": session_id}

async def process_translation(session_id: str, file_path: Path, language: str):
    """Translate the content of the uploaded file."""
    try:
        await websocket_manager.broadcast("Reading file content...")
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()

        await websocket_manager.broadcast("Translating file content...")
        translated_text = await translate_text(content, language)

        # Save translated file
        translated_file = file_path.with_suffix(".translated.txt")
        with translated_file.open("w", encoding="utf-8") as file:
            file.write(translated_text)

        # Notify WebSocket and save history
        await websocket_manager.broadcast(f"Translation completed: {translated_file.name}")
        save_file_history(session_id, file_path.name, translated_file.name, language, "Success")

    except Exception as e:
        await websocket_manager.broadcast(f"Translation failed: {e}")

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        await websocket_manager.disconnect(websocket)

@app.get("/history/")
async def file_history(session_id: str):
    """Fetch and display file history."""
    history = get_file_history(session_id)
    if not history:
        return {"message": "No history found for this session ID."}
    return TEMPLATES.TemplateResponse("history.html", {"request": {}, "history": history})

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    """Download a translated file."""
    file_path = UPLOAD_DIR / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path)
