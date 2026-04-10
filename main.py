from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from bson import ObjectId
from datetime import datetime
import asyncio

from db import collection
from models import Note

app = FastAPI()

# 📁 Static files (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 📁 Templates
templates = Jinja2Templates(directory="templates")

# ================= UTILS =================

def serialize_note(note):
    return {
        "id": str(note["_id"]),
        "text": note["text"],
        "created_at": note.get("created_at"),
        "updated_at": note.get("updated_at")
    }

# ================= UI =================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    notes = [serialize_note(n) for n in collection.find().sort("created_at", -1)]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "notes": notes
    })


@app.post("/add")
def add_from_ui(text: str = Form(...)):
    note = Note(text=text)
    collection.insert_one(note.model_dump())
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{note_id}")
def delete_note(note_id: str):
    try:
        result = collection.delete_one({"_id": ObjectId(note_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    return RedirectResponse("/", status_code=303)


@app.post("/update/{note_id}")
def update_note(note_id: str, text: str = Form(...)):
    try:
        result = collection.update_one(
            {"_id": ObjectId(note_id)},
            {
                "$set": {
                    "text": text,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    return RedirectResponse("/", status_code=303)


# ================= API =================

@app.post("/add-note")
def add_note(note: Note):
    collection.insert_one(note.model_dump())
    return {"message": "Note added successfully"}


@app.get("/notes")
def get_notes():
    notes = [serialize_note(n) for n in collection.find().sort("created_at", -1)]
    return notes


@app.get("/note/{note_id}")
def get_note(note_id: str):
    try:
        note = collection.find_one({"_id": ObjectId(note_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return serialize_note(note)


@app.get("/summary/{note_id}")
def summary(note_id: str):
    try:
        note = collection.find_one({"_id": ObjectId(note_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    words = note["text"].split()
    return {"summary": " ".join(words[:10])}


@app.get("/wordcount/{note_id}")
def wordcount(note_id: str):
    try:
        note = collection.find_one({"_id": ObjectId(note_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"count": len(note["text"].split())}


# ================= EXTRA =================

@app.get("/slow")
async def slow():
    await asyncio.sleep(2)
    return {"message": "Async working!"}