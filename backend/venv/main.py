from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "MemoGraph backend running 🚀"}

@app.get("/test")
def test():
    return {"status": "working"}
