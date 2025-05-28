from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import shutil
import uuid
from merchant_risk_tool import run_pipeline  # Must return (clean_file, risk_file, logs)

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/risk-assessment/")
async def assess_risk(request: Request, file: UploadFile = File(...)):
    try:
        # Generate unique filename
        unique_id = uuid.uuid4().hex
        original_filename = file.filename.replace(" ", "_")
        uploaded_filename = f"{unique_id}_{original_filename}"
        input_path = os.path.join(UPLOAD_DIR, uploaded_filename)

        # Save uploaded file
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run the pipeline and capture logs
        clean_file, risk_file, logs = run_pipeline(input_path, OUTPUT_DIR)

        base_url = str(request.base_url).rstrip("/")

        return {
            "clean_file": f"{base_url}/download/{os.path.basename(clean_file)}",
            "risk_report": f"{base_url}/download/{os.path.basename(risk_file)}",
            "logs": logs  # Sent to frontend terminal
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/download/{filename}")
async def download(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)