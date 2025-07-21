from langchain.tools import tool
import json
from typing import Union
import tempfile
import os
from test import main as extract_diet_report
import pytesseract

# Set the path to the local tesseract binary (Linux typical path)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

@tool("extract_diet_report_from_image", return_direct=True)
def extract_diet_report_tool(image: Union[str, bytes]) -> str:
    """
    Extracts diet/body composition report data from an image file (path or bytes) and returns JSON.
    Args:
        image: Path to the image file or image bytes.
    Returns:
        JSON string with extracted report data.
    """
    # Handle image input (path or bytes)
    if isinstance(image, bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(image)
            tmp_path = tmp.name
        image_path = tmp_path
    elif isinstance(image, str):
        image_path = image
    else:
        return json.dumps({"error": "Invalid image input type."})

    try:
        result = extract_diet_report(image_path)
        if not result:
            return json.dumps({"error": "No data extracted."})
        return json.dumps(result, ensure_ascii=False, indent=2)
    finally:
        # Clean up temp file if used
        if isinstance(image, bytes) and os.path.exists(image_path):
            os.remove(image_path)
