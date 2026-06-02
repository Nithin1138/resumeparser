from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from parser import parse_resume, parse_text

app = FastAPI(
    title="Resume Parser API",
    description="Parse PDF/DOCX resumes and extract structured data: name, email, phone, skills, experience, education and more.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Resume Parser API is running."}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "version": "1.0.0"}


# ── Main parse endpoint ───────────────────────────────────────────────────────

@app.post("/parse", tags=["Resume"])
async def parse(
    file: str,
):
    """
    Upload a resume string and get back structured JSON with:
    - name, email, phone, LinkedIn, GitHub
    - skills list
    - years of experience
    - sections: summary, experience, education, projects, certifications
    """

    start = time.time()
    try:
        result = parse_text(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    elapsed = round(time.time() - start, 3)

    return JSONResponse({
        "success": True,
        "processing_time_seconds": elapsed,
        "data": result,
    })


# ── Batch endpoint (paid tier feature) ───────────────────────────────────────

@app.post("/parse/batch", tags=["Resume"])
async def parse_batch(
    files: list[UploadFile] = File(..., description="Multiple resume files (max 10)"),
):
    """
    Parse up to 10 resumes in one request. Returns array of results.
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Max 10 files per batch request.")

    results = []
    for f in files:
        file_bytes = await f.read()
        try:
            data = parse_resume(file_bytes, f.filename)
            results.append({"filename": f.filename, "success": True, "data": data})
        except Exception as e:
            results.append({"filename": f.filename, "success": False, "error": str(e)})

    return JSONResponse({"total": len(results), "results": results})
