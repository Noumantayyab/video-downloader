import os
import uuid
import re
import io
import requests

from pathlib import Path
from urllib.parse import urljoin
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
from fastapi.responses import StreamingResponse
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from fastapi import File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.responses import HTMLResponse



app = FastAPI()

# Directories
BASE_DIR     = Path(__file__).resolve().parent
STATIC_DIR   = BASE_DIR / "static"
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    idx = STATIC_DIR / "index.html"
    if not idx.exists():
        raise HTTPException(status_code=500, detail="index.html not found")
    # Force UTF-8 decoding of your CSS-rich HTML
    return idx.read_text(encoding="utf-8")



def serve_and_cleanup(path: str):
    if not os.path.isfile(path):
        raise HTTPException(status_code=500, detail="Downloaded file not found.")
    def cleanup(p: str):
        try:
            os.remove(p)
        except OSError:
            pass
    resp = FileResponse(
        path=path,
        filename=Path(path).name,
        media_type="application/octet-stream"
    )
    resp.background = BackgroundTask(cleanup, path)
    return resp


@app.get("/download")
def download_youtube(url: str = Query(..., description="YouTube video URL")):
    temp = DOWNLOAD_DIR / f"{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        "format": "best",
        "outtmpl": str(temp),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn   = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"YouTube error: {e}")
    return serve_and_cleanup(fn)


@app.get("/download_instagram")
def download_instagram(url: str = Query(..., description="Instagram video URL")):
    temp = DOWNLOAD_DIR / f"{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(temp),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn   = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instagram error: {e}")
    return serve_and_cleanup(fn)


@app.get("/download_twitter")
def download_twitter(url: str = Query(..., description="X (Twitter) video URL")):
    temp = DOWNLOAD_DIR / f"{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(temp),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn   = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Twitter error: {e}")
    return serve_and_cleanup(fn)


@app.get("/download_facebook")
def download_facebook(url: str = Query(..., description="Facebook video URL")):
    temp = DOWNLOAD_DIR / f"{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(temp),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn   = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Facebook error: {e}")
    return serve_and_cleanup(fn)


@app.get("/download_tiktok")
def download_tiktok(url: str = Query(..., description="TikTok video URL")):
    temp = DOWNLOAD_DIR / f"{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(temp),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn   = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"TikTok error: {e}")
    return serve_and_cleanup(fn)


@app.get("/probe_other")
def probe_other(url: str = Query(..., description="Any page to scan for videos")):
    try:
        r = requests.get(url, timeout=10, verify=False)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fetch error: {e}")

    soup = BeautifulSoup(r.text, "html.parser")
    sources = set()

    def extract(doc):
        for vid in doc.find_all("video"):
            if s := vid.get("src"):
                sources.add(s)
            for src in vid.find_all("source"):
                if t := src.get("src"):
                    sources.add(t)
        for src in doc.find_all("source"):
            if t := src.get("src"):
                sources.add(t)

    extract(soup)
    if iframe := soup.find("iframe", id="playit"):
        src = iframe.get("src")
        if src:
            try:
                r2 = requests.get(urljoin(url, src), timeout=10, verify=False)
                r2.raise_for_status()
                extract(BeautifulSoup(r2.text, "html.parser"))
            except:
                pass

    # Return absolute URLs
    return [urljoin(url, s) for s in sources]


@app.get("/download_other")
def download_other(url: str = Query(..., description="Direct video file URL")):
    """
    Streams any direct video file back to the user.
    """
    temp = DOWNLOAD_DIR / f"{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        "format": "best[ext=mp4]+bestaudio/best",
        "outtmpl": str(temp),
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn   = ydl.prepare_filename(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Generic error: {e}")
    return serve_and_cleanup(fn)

# serve the thumbnail page
@app.get("/thumbnail", response_class=HTMLResponse)
def thumbnail_page():
    tpl = STATIC_DIR / "thumbnail.html"
    if not tpl.exists():
        raise HTTPException(500, "thumbnail.html not found")
    return tpl.read_text()

# download the thumbnail
@app.get("/download_thumbnail")
def download_thumbnail(url: str = Query(..., description="YouTube video URL")):
    """
    Extract the video ID, fetch the maxres thumbnail (or fallback), 
    and stream it back as an image download.
    """
    # extract video ID
    m = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{6,12})", url)
    if not m:
        raise HTTPException(400, "Invalid YouTube URL")
    vid = m.group(1)

    # try maxres, then high quality
    thumbs = [
        f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
    ]
    for thumb_url in thumbs:
        resp = requests.get(thumb_url, stream=True)
        if resp.status_code == 200 and resp.headers.get("content-type","").startswith("image"):
            # stream back with correct filename
            filename = f"{vid}_thumbnail.jpg"
            return StreamingResponse(
                resp.raw,
                media_type=resp.headers.get("content-type"),
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    raise HTTPException(404, "Thumbnail not found")


# platform dimensions map
PLATFORMS = {
    "facebook":  (360, 360),
    "whatsapp":  (500, 500),
    "instagram": (320, 320),
    "linkedin":  (400, 400),
}

@app.get("/profile", response_class=HTMLResponse)
def profile_page():
    tpl = STATIC_DIR / "profile.html"
    if not tpl.exists():
        raise HTTPException(status_code=500, detail="profile.html not found")
    return tpl.read_text()


# platform dimensions map
PLATFORMS = {
    "facebook":  (360, 360),
    "whatsapp":  (500, 500),
    "instagram": (320, 320),
    "linkedin":  (400, 400),
}

@app.post("/resize_profile")
async def resize_profile(
    platform: str = Form(..., description="Target platform"),
    file: UploadFile = File(...),
):
    if platform not in PLATFORMS:
        raise HTTPException(400, "Unknown platform")

    try:
        img = Image.open(io.BytesIO(await file.read()))
    except Exception:
        raise HTTPException(400, "Invalid image file")

    target_w, target_h = PLATFORMS[platform]
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top  = (h - side) // 2

    img_cropped = img.crop((left, top, left + side, top + side))
    img_resized = img_cropped.resize((target_w, target_h), Image.LANCZOS)

    buf = io.BytesIO()
    img_resized.save(buf, format="JPEG", quality=95)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"attachment; filename=profile_{platform}.jpg"}
    )


@app.get("/palette", response_class=HTMLResponse)
def palette_page():
    tpl = STATIC_DIR / "palette.html"
    if not tpl.exists():
        raise HTTPException(status_code=500, detail="palette.html not found")
    return tpl.read_text()


@app.get("/resume_fill", response_class=HTMLResponse)
def resume_fill_page():
    tpl = STATIC_DIR / "resume_fill.html"
    if not tpl.exists():
        raise HTTPException(500, "resume_fill.html not found")
    return tpl.read_text()

@app.get("/css_playground", response_class=HTMLResponse)
def css_animation_playground():
    tpl = STATIC_DIR / "css_playground.html"
    if not tpl.exists():
        raise HTTPException(500, "css_playground.html not found")
    return tpl.read_text()