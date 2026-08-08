from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from datetime import datetime
import os
import json
import math

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

DATA_DIR = "data"
MEMORY_DIR = "memory_units"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)


class SearchRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {"message": "MemoGraph backend running 🚀"}


@app.get("/test")
def test():
    return {"status": "working"}


def chunk_text(text, chunk_size=500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    return dot_product / (magnitude1 * magnitude2)


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

    chunks = chunk_text(text)

    memory_units = []

    for index, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()

        memory_unit = {
            "id": f"{file.filename}_chunk_{index + 1}",
            "source_file": file.filename,
            "chunk_index": index + 1,
            "content": chunk,
            "embedding": embedding,
            "created_at": datetime.now().isoformat()
        }

        memory_units.append(memory_unit)

    memory_file_path = os.path.join(
        MEMORY_DIR,
        file.filename.replace(".txt", "_memory.json")
    )

    with open(memory_file_path, "w", encoding="utf-8") as f:
        json.dump(memory_units, f, indent=4)

    return {
        "filename": file.filename,
        "stored_at": file_path,
        "memory_file": memory_file_path,
        "total_chunks": len(memory_units),
        "first_chunk_preview": memory_units[0]["content"][:200] if memory_units else "",
        "message": "Memory units created successfully!"
    }


@app.post("/search")
def search_memory(request: SearchRequest):
    query_embedding = model.encode(request.query).tolist()

    results = []

    for filename in os.listdir(MEMORY_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(MEMORY_DIR, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                memory_units = json.load(f)

            for memory in memory_units:
                similarity = cosine_similarity(query_embedding, memory["embedding"])

                results.append({
                    "source_file": memory["source_file"],
                    "chunk_index": memory["chunk_index"],
                    "content": memory["content"],
                    "similarity": round(similarity, 4)
                })

    results = sorted(results, key=lambda x: x["similarity"], reverse=True)

    return {
        "query": request.query,
        "top_results": results[:5]
    }