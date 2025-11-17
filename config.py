import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Folders
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "downloads"))
MARKDOWN_DIR = Path(os.getenv("MARKDOWN_DIR", "markdown_output"))

# Excel file
EXCEL_PATH = os.getenv("EXCEL_PATH", "demo.xlsx")

# Chandra OCR
CHANDRA_API_KEY = os.getenv("CHANDRA_API_KEY")
CHANDRA_URL = os.getenv("CHANDRA_URL", "https://api.chandra.run/v1/ocr")
