from fastapi import FastAPI, UploadFile, File, HTTPException
import os

app = FastAPI()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "MemoGraph backend running 🚀"}


@app.get("/test")
def test():
    return {"status": "working"}


@app.post("/upload-text")
async def upload_text_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files allowed")

    content = await file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid text file")

    file_path = os.path.join(DATA_DIR, file.filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return {
        "filename": file.filename,
        "stored_at": file_path,
        "content_length": len(text),
        "preview": text[:300],
        "message": "Memory stored successfully!"
    }