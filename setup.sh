#!/bin/bash
# Setup script for diet server

echo "Setting up Diet Server..."

# Check if running as root or with sudo for system packages
if [ "$EUID" -ne 0 ]; then
    echo "Note: You may need to run with sudo for system package installation"
    echo "Or run: sudo apt update && sudo apt install -y tesseract-ocr tesseract-ocr-eng"
    echo ""
fi

# Install system dependencies (Tesseract OCR)
echo "Installing system dependencies..."
if command -v apt &> /dev/null; then
    # Ubuntu/Debian
    echo "Detected apt package manager (Ubuntu/Debian)"
    if [ "$EUID" -eq 0 ]; then
        apt update
        apt install -y tesseract-ocr tesseract-ocr-eng python3-venv python3-pip
    else
        echo "Installing Tesseract OCR (requires sudo)..."
        sudo apt update
        sudo apt install -y tesseract-ocr tesseract-ocr-eng python3-venv python3-pip
    fi
elif command -v yum &> /dev/null; then
    # CentOS/RHEL/Fedora
    echo "Detected yum package manager (CentOS/RHEL)"
    if [ "$EUID" -eq 0 ]; then
        yum install -y tesseract tesseract-langpack-eng python3 python3-pip python3-venv
    else
        sudo yum install -y tesseract tesseract-langpack-eng python3 python3-pip python3-venv
    fi
elif command -v dnf &> /dev/null; then
    # Fedora
    echo "Detected dnf package manager (Fedora)"
    if [ "$EUID" -eq 0 ]; then
        dnf install -y tesseract tesseract-langpack-eng python3 python3-pip python3-venv
    else
        sudo dnf install -y tesseract tesseract-langpack-eng python3 python3-pip python3-venv
    fi
elif command -v pacman &> /dev/null; then
    # Arch Linux
    echo "Detected pacman package manager (Arch Linux)"
    if [ "$EUID" -eq 0 ]; then
        pacman -S --noconfirm tesseract tesseract-data-eng python python-pip
    else
        sudo pacman -S --noconfirm tesseract tesseract-data-eng python python-pip
    fi
else
    echo "Package manager not detected. Please install Tesseract OCR manually:"
    echo "- Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-eng"
    echo "- CentOS/RHEL: sudo yum install tesseract tesseract-langpack-eng"
    echo "- Fedora: sudo dnf install tesseract tesseract-langpack-eng"
    echo "- Arch: sudo pacman -S tesseract tesseract-data-eng"
fi

# Verify Tesseract installation
echo "Verifying Tesseract installation..."
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract is installed: $(tesseract --version | head -n1)"
else
    echo "✗ Tesseract installation failed. Please install manually."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "To run the server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
echo "3. Or use uvicorn directly: uvicorn app.main:app --reload"
echo ""
echo "The server will be available at: http://localhost:8000"
echo "API documentation will be available at: http://localhost:8000/docs"
