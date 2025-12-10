from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from browser_client.pipeline import generate_code_from_raw_text

app = FastAPI()

# ==== FRONTEND SERVING SETUP ====

BASE_DIR = os.path.dirname(os.path.dirname(__file__))         # D:\PseudoCode
FRONTEND_DIR = os.path.join(BASE_DIR, "browser_client")       # path to index.html

# Serve static frontend files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Show index.html when user opens "/"
@app.get("/", include_in_schema=False)
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ==== API ====

class GenerateRequest(BaseModel):
    text: str


@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    result = generate_code_from_raw_text(req.text)
    return {
        "code": result.get("code", ""),
        "meta": result
    }
