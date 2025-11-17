import asyncio
import pandas as pd
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    EXCEL_PATH,
    DOWNLOAD_DIR,
    MARKDOWN_DIR,
    CHANDRA_API_KEY,
    CHANDRA_URL,
)

from downloader import download_pdf
from logger import logger

# -----------------------
# SESSION MANAGEMENT
# -----------------------
def _create_session_with_retries(retries=2, backoff=0.3, status_forcelist=(500,502,503,504)):
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=status_forcelist, allowed_methods=["POST","GET"])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

# -----------------------
# SEND TO CHANDRA OCR
# -----------------------
def send_to_chandra(pdf_path: Path) -> str:
    logger.info(f"Sending to Chandra OCR: {pdf_path.name}")

    if not CHANDRA_API_KEY or not CHANDRA_URL:
        logger.error("Missing CHANDRA_API_KEY or CHANDRA_URL. Set environment/config correctly.")
        return ""

    if not pdf_path or not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return ""

    session = _create_session_with_retries()
    headers = {"Authorization": f"Bearer {CHANDRA_API_KEY}"}

    try:
        with pdf_path.open("rb") as f:
            resp = session.post(CHANDRA_URL, headers=headers, files={"file": f}, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"OCR request failed for {pdf_path.name}: {exc}")
        return ""

    try:
        data = resp.json()
    except ValueError as exc:
        logger.error(f"Invalid JSON response from OCR for {pdf_path.name}: {exc}")
        return ""

    md = data.get("markdown", "")
    if not md:
        logger.warning(f"OCR returned empty markdown for {pdf_path.name}")
    return md

# -----------------------
# SAVE OUTPUT MARKDOWN
# -----------------------
def save_markdown(pdf_path: Path, markdown_text: str):
    try:
        MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
        md_path = MARKDOWN_DIR / (pdf_path.stem + ".md")
        # simple atomic-ish write: write to temp then rename
        tmp = md_path.with_suffix(".md.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            f.write(markdown_text or "")
        tmp.replace(md_path)
        logger.info(f"Saved markdown: {md_path.name}")
    except Exception as exc:
        logger.exception(f"Failed saving markdown for {getattr(pdf_path, 'name', str(pdf_path))}: {exc}")

# -----------------------
# MAIN PIPELINE
# -----------------------
async def main():
    try:
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

        excel_path = Path(EXCEL_PATH)
        if not excel_path.exists():
            logger.error(f"Excel file not found: {excel_path}")
            return

        try:
            df = pd.read_excel(excel_path)
        except Exception as exc:
            logger.exception(f"Failed to read Excel {excel_path}: {exc}")
            return

        col = "Final Invoice Link"
        if col not in df.columns:
            logger.error(f"Expected column '{col}' not found in Excel. Columns: {list(df.columns)}")
            return

        urls = df[col].dropna().tolist()

        for url in urls:
            # per-item protection to avoid stopping whole run
            try:
                if not isinstance(url, str) or not url.strip():
                    logger.warning(f"Skipping invalid url value: {url}")
                    continue

                try:
                    pdf_path = await download_pdf(url)
                except Exception as e:
                    logger.exception(f"Failed to download from {url}: {e}")
                    continue

                if not pdf_path:
                    logger.warning(f"No pdf returned for {url}")
                    continue

                # run blocking OCR call off the event loop
                try:
                    md_text = await asyncio.to_thread(send_to_chandra, pdf_path)
                except Exception as exc:
                    logger.exception(f"send_to_chandra failed for {pdf_path}: {exc}")
                    continue

                try:
                    await asyncio.to_thread(save_markdown, pdf_path, md_text)
                except Exception as exc:
                    logger.exception(f"save_markdown failed for {pdf_path}: {exc}")
                    continue

            except Exception as exc:
                logger.exception(f"Unexpected error processing url {url}: {exc}")
                continue
    except Exception as exc:
        logger.exception(f"Unexpected fatal error in main pipeline: {exc}")

# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    try:
        logger.info("==> Starting Playwright Chandra OCR <==")
        asyncio.run(main())
    except Exception as exc:
        logger.exception(f"Unhandled exception during run: {exc}")