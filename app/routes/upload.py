import os
import uuid
import httpx
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse

router = APIRouter(prefix="/upload", tags=["upload"])

DISK_ROOT = "/var/data/disk"
os.makedirs(DISK_ROOT, exist_ok=True)


def _dish_dir(category_id: int, dish_id: int) -> str:
    path = os.path.join(DISK_ROOT, str(category_id), str(dish_id))
    os.makedirs(path, exist_ok=True)
    return path


def _clear_dish_images(category_id: int, dish_id: int):
    """Remove all existing images for a dish."""
    d = os.path.join(DISK_ROOT, str(category_id), str(dish_id))
    if os.path.isdir(d):
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if os.path.isfile(fp):
                os.remove(fp)


@router.post("/dish-image")
async def upload_dish_image(
    file: UploadFile = File(...),
    category_id: int = Form(...),
    dish_id: int = Form(...),
):
    """Upload an image file from the user's computer."""
    _clear_dish_images(category_id, dish_id)
    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(_dish_dir(category_id, dish_id), filename)
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
    url = f"/api/upload/dish-image/{category_id}/{dish_id}/{filename}"
    return {"url": url}


@router.post("/dish-image-url")
async def upload_dish_image_from_url(
    category_id: int = Form(...),
    dish_id: int = Form(...),
    url: str = Form(...),
):
    """Download an image from a URL and save it locally."""
    _clear_dish_images(category_id, dish_id)
    ext = ".jpg"
    for e in [".png", ".webp", ".gif", ".jpeg", ".jpg"]:
        if e in url.lower():
            ext = e
            break
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(_dish_dir(category_id, dish_id), filename)
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            f.write(resp.content)
    saved_url = f"/api/upload/dish-image/{category_id}/{dish_id}/{filename}"
    return {"url": saved_url}


@router.delete("/dish-image/{category_id}/{dish_id}")
def delete_dish_image(category_id: int, dish_id: int):
    """Delete all images for a dish."""
    _clear_dish_images(category_id, dish_id)
    return {"ok": True}


@router.get("/dish-image/{category_id}/{dish_id}/{filename}")
def get_dish_image(category_id: int, dish_id: int, filename: str):
    path = os.path.join(DISK_ROOT, str(category_id), str(dish_id), filename)
    if not os.path.exists(path):
        return {"error": "not found"}
    return FileResponse(path, headers={"Access-Control-Allow-Origin": "*"})


# Legacy: keep old upload endpoint working
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"url": f"/api/upload/files/{filename}"}


@router.get("/files/{filename}")
def get_file(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        return {"error": "not found"}
    return FileResponse(path, headers={"Access-Control-Allow-Origin": "*"})
