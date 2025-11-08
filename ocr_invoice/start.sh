#!/bin/bash

# Exit immediately on errors
set -e

mkdir -p /home/cxloop/ocr/logs
echo "Launcher triggered at: $(date)" >> /home/cxloop/ocr/logs/ocr_launcher_trace.log

# Define project directory
PROJECT_DIR=/home/cxloop/ocr/
LOG_DIR="$PROJECT_DIR/logs"
#SRC_DIR="$PROJECT_DIR/src"

# Navigate to project directory
cd "$PROJECT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install system Tesseract OCR engine (Debian/Ubuntu via apt-get)
# This requires sudo unless the script is run as root.
if command -v apt-get >/dev/null 2>&1; then
    echo "Attempting to install tesseract OCR system packages via apt-get..." >> "$LOG_DIR/ocr_launcher_trace.log"
    if [ "$(id -u)" -eq 0 ]; then
        apt-get update >> "$LOG_DIR/ocr_launcher_trace.log" 2>&1
        apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-eng >> "$LOG_DIR/ocr_launcher_trace.log" 2>&1
    else
        echo "Running apt-get with sudo (you may be prompted for your password)..." >> "$LOG_DIR/ocr_launcher_trace.log"
        sudo apt-get update >> "$LOG_DIR/ocr_launcher_trace.log" 2>&1
        sudo apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-eng >> "$LOG_DIR/ocr_launcher_trace.log" 2>&1
    fi
else
    echo "apt-get not found on this system; skipping automatic tesseract installation. Please install tesseract manually." >> "$LOG_DIR/ocr_launcher_trace.log"
fi

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run Streamlit client in background, logging output
nohup streamlit run app.py --server.port 8501 > "$LOG_DIR/streamlit.log" 2>&1 &