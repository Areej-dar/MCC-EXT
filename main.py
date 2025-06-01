from fastapi import FastAPI, UploadFile, File, Request, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
import uvicorn
import shutil
import uuid
import requests
from dotenv import load_dotenv
from merchant_risk_tool import run_pipeline  # Must return (clean_file, risk_file, logs)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


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
    
@app.get("/search_google")
def search_google(q: str = Query(...)):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": q
    }
    response = requests.get(url, params=params)
    return response.json()

@app.get("/search_openai")
def search_openai(q: str = Query(...)):
    try:
        system_prompt = """
        You are a risk-analysis assistant for SadaPay.
        Input: merchant name, country code.
        Output *only* this JSON:
        {
        "risk_level":"Low|Medium|High",
        "risk_score":0-100,
        "website":"<inferred or provided domain or null>",
        "summary":"one-sentence findings",
        "business_nature":"Briefly explain what the merchant does or offers",
        "reason":"brief rationale for the level",
        "confidence":0-100
        }
        Rules:
        1. If “domain” is empty, try to infer the merchant’s website and put it in `website`.
        2. Blacklist if business involves: weapons, arms, adult content, gambling, scam, phishing, hacking, forex, crypto, trading, fundraising, charity, donations.
        3. Base your score on:
        • domain validity
        • presence of pages: About Us, Contact Us, Privacy Policy, T&C, Refund Policy
        • social links (Facebook, Twitter, LinkedIn, Instagram, YouTube)
        • red-flag marketing terms
        4. If you can’t infer a domain, set `"website": null` and say so in `summary`.
        5. Tell the merchant category (e.g. “e-commerce”, “gaming”) in `summary`.
        """.strip()

        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": q}
            ],
            temperature=0.3
        )

        return {
            "results": [
                {
                    "title": "AI Risk Analysis",
                    "description": response["choices"][0]["message"]["content"]
                }
            ]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
