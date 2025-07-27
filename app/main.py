from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import reports

app = FastAPI(
    title="Body Composition Analysis Report Extractor API",
    description="API for extracting data from body composition analysis reports",
    version="1.0.0"
)

# Set your tesseract path here if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Body Composition Analysis Report Extractor API. Use /api/v1/extract_report/ to upload an image."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}