from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os

from app.utils import extract_report


router = APIRouter()

@router.get("/")
async def get_reports_info():
    """
    GET all reports
    """
    return {
        "message": "Reports API",
        "endpoints": {
            "/extract_report/": "POST - Upload an image file to extract report data"
        },
        "supported_formats": [".jpg", ".jpeg", ".png"]
    }


@router.post("/extract_report/")
async def extract_report_api(file: UploadFile = File(...)):
    """
    Extract data from a body composition analysis report image.
    
    Args:
        file: Image file (jpg, jpeg, png)
        
    Returns:
        JSON containing extracted report data
    """
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only image files (.jpg, .jpeg, .png) are supported.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Extract the report using the convenience function
        data = extract_report(tmp_path)
        os.remove(tmp_path)
        
        return JSONResponse(content={
            # "success": True,
            # "filename": file.filename,
            "data": data
        })
    except Exception as e:
        # Clean up temp file if it exists
        try:
            os.remove(tmp_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.post("/extract_report/url/")
async def extract_report_from_url(image_url: str):
    """
    Extract data from a body composition analysis report image via URL.
    
    Args:
        image_url: URL to the image file
        
    Returns:
        JSON containing extracted report data
    """
    import requests
    
    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        # Extract the report
        data = extract_report(tmp_path)
        os.remove(tmp_path)
        
        return JSONResponse(content={
            # "success": True,
            # "image_url": image_url,
            "data": data
        })
    except Exception as e:
        # Clean up temp file if it exists
        try:
            os.remove(tmp_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error processing image from URL: {str(e)}")