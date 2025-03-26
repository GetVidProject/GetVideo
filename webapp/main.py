
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import uvicorn
import os
import uuid
import json
from collections import defaultdict
from datetime import datetime

from handlers.function import download_and_send_media, generate_url_id
import url_storage as storage

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
templates = Jinja2Templates(directory="webapp/templates")

progress_file = "progress.json"
log_file = "log.json"
ADMIN_ID = "1249610916"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/progress")
async def get_progress():
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            return JSONResponse(content=json.load(f))
    return JSONResponse(content={"percent": 0})

@app.post("/auth")
async def auth(request: Request):
    data = await request.json()
    request.session["user"] = data
    return {"success": True}

@app.post("/download", response_class=HTMLResponse)
async def process(request: Request, url: str = Form(...), quality: str = Form(None), format: str = Form(None)):
    url_id = generate_url_id(url)
    chat_id = request.session.get("user", {}).get("id", 0)

    def progress_hook(d):
        if d.get("status") == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                with open(progress_file, "w") as f:
                    json.dump({"percent": int(float(percent))}, f)
            except:
                pass
        elif d.get("status") == "finished":
            with open(progress_file, "w") as f:
                json.dump({"percent": 100}, f)

    try:
        await download_and_send_media(
            bot=None,
            chat_id=chat_id,
            url=url,
            media_type="video" if quality else "audio",
            quality=quality,
            audio_format=format,
            progress_hook=progress_hook
        )
        return templates.TemplateResponse("done.html", {"request": request, "message": "✅ Download complete!"})
    except Exception as e:
        return templates.TemplateResponse("done.html", {"request": request, "message": f"❌ Error: {e}"})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    user = request.session.get("user")
    if not user or str(user.get("id")) != ADMIN_ID:
        return HTMLResponse("<h2 style='color:red;text-align:center'>⛔ Access denied.</h2>", status_code=403)

    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)

    # Статистика по дням
    counts = defaultdict(lambda: {"video": 0, "audio": 0})
    for log in logs:
        date = log["timestamp"][:10]
        if log["type"] == "video":
            counts[date]["video"] += 1
        else:
            counts[date]["audio"] += 1

    labels = sorted(counts.keys())
    video_counts = [counts[day]["video"] for day in labels]
    audio_counts = [counts[day]["audio"] for day in labels]

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "logs": sorted(logs, key=lambda x: x["timestamp"], reverse=True),
        "stats": {
            "labels": labels,
            "video": video_counts,
            "audio": audio_counts
        }
    })

@app.get("/admin/download")
async def download_logs():
    return FileResponse(log_file, filename="log.json", media_type="application/json")

if __name__ == "__main__":
    uvicorn.run("webapp.main:app", host="0.0.0.0", port=8000)
