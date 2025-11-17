from pathlib import Path
import os
import sys
from loguru import logger

LOG_DIR = Path(os.getenv("LOG_DIR", Path(__file__).parent / "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "chandra_ocr.log"

# remove default handler and add stderr + file handlers
logger.remove()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger.add(sys.stderr, level=LOG_LEVEL, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add(str(LOG_FILE), rotation="10 MB", retention="7 days", level=LOG_LEVEL, backtrace=True, diagnose=True, encoding="utf-8")
