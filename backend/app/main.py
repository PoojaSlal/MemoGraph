from fastapi import FastAPI

app = FastAPI(
    title="MemoGraph API",
    version="0.1.0",
    description="Context-aware personal AI memory retrieval system.",
)


@app.get("/")
def root():
    return {
        "name": "MemoGraph",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/test")
def test():
    return {
        "status": "working"
    }