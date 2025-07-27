# Diet Server - Body Composition Analysis Report Extractor

A FastAPI-based web service for extracting data from body composition analysis report images using OCR (Optical Character Recognition).

## Features

- Extract structured data from body composition analysis report images
- Support for multiple image formats (JPG, JPEG, PNG)
- RESTful API with automatic documentation
- Image upload via file or URL
- Comprehensive error handling
- CORS support for web applications

## Prerequisites

- Python 3.8 or higher
- Tesseract OCR
- OpenCV dependencies

## Quick Setup

### Automated Setup (Recommended)

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd diet_server
   ```
3. Run the setup script:
   ```bash
   ./setup.sh
   ```

The setup script will automatically:
- Install Tesseract OCR and system dependencies
- Create a Python virtual environment
- Install all required Python packages

### Manual Setup

If you prefer to set up manually or the automated script doesn't work for your system:

1. **Install Tesseract OCR:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install tesseract-ocr tesseract-ocr-eng
   
   # CentOS/RHEL
   sudo yum install tesseract tesseract-langpack-eng
   
   # Fedora
   sudo dnf install tesseract tesseract-langpack-eng
   
   # Arch Linux
   sudo pacman -S tesseract tesseract-data-eng
   
   # macOS (with Homebrew)
   brew install tesseract
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Option 1: Using the run script
```bash
source venv/bin/activate
python run.py
```

### Option 2: Using uvicorn directly
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI JSON schema:** http://localhost:8000/openapi.json

## API Endpoints

### GET /
Welcome message and basic info

### GET /health
Health check endpoint

### GET /api/v1/
Reports API information

### POST /api/v1/extract_report/
Extract data from uploaded image file

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file: .jpg, .jpeg, .png)

**Response:**
```json
{
  "success": true,
  "filename": "report.jpg",
  "data": {
    "report_title": "Body composition analysis report",
    "report_date": "2025-01-15 10:30",
    "basic_data": {
      "name": "John",
      "gender": "Male",
      "height_cm": 175,
      "age": 30,
      "current_weight": "70.5kg",
      "weight_change": {
        "direction": "increase",
        "value": 1.2
      },
      "bmi": {"value": 23.0},
      "body_fat_percentage": {"value": 15.2},
      "muscle_rate": {"value": 42.8}
    },
    "body_composition_analysis": {
      "fat_mass": {"value": 10.6, "unit": "kg"},
      "moisture": {"value": 62.3, "unit": "%"},
      "protein_a": {"value": 12.1, "unit": "kg"},
      "bone_mass": {"value": 3.2, "unit": "kg"}
    },
    "weight_control": {
      "current_weight_kg": 70.5,
      "standard_weight_kg": 68.3,
      "muscle_mass_kg": 56.8,
      "lean_body_mass_kg": 59.9,
      "weight_control_kg": 2.2
    },
    "body_type": {
      "overall": "Standard"
    },
    "other_indicators": {
      "bmr": {"value": "1680"},
      "visceral_fat_level": {"value": "5"},
      "subcutaneous_fat_level": {"value": "12"},
      "body_age": {"value": "28"},
      "obesity_rating": {"value": "Standard"},
      "protein_rate": {"value": "17.2"}
    }
  }
}
```

### POST /api/v1/extract_report/url/
Extract data from image URL

**Request:**
- Method: POST
- Content-Type: application/json
- Body: `{"image_url": "https://example.com/report.jpg"}`

## Error Handling

The API returns appropriate HTTP status codes:
- **200:** Success
- **400:** Bad Request (invalid file format, missing parameters)
- **500:** Internal Server Error (processing errors, file access issues)

## Development

### Project Structure
```
diet_server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── utils.py             # OCR and image processing utilities
│   └── routers/
│       ├── __init__.py
│       └── reports.py       # Reports API endpoints
├── requirements.txt         # Python dependencies
├── setup.sh                # Automated setup script
├── run.py                  # Application runner
└── README.md               # This file
```

### Adding New Features

1. Create new router modules in `app/routers/`
2. Import and include them in `app/main.py`
3. Add utility functions in `app/utils.py`
4. Update `requirements.txt` for new dependencies

## Troubleshooting

### Common Issues

1. **Tesseract not found:**
   - Ensure Tesseract is installed and in your system PATH
   - On some systems, you may need to specify the path in `app/main.py`

2. **Import errors:**
   - Make sure the virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

3. **Permission errors:**
   - Ensure the setup script has execute permissions: `chmod +x setup.sh`
   - For system package installation, run with sudo if needed

4. **Port already in use:**
   - Change the port in `run.py` or use: `uvicorn app.main:app --port 8001`

### Tesseract Configuration

If Tesseract is installed in a non-standard location, uncomment and modify this line in `app/main.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'
```

## License

This project is provided as-is for educational and development purposes.
