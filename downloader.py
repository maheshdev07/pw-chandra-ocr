import base64
from pathlib import Path
from playwright.async_api import async_playwright
from config import DOWNLOAD_DIR
from logger import logger

async def download_pdf(url):
    logger.info(f"Opening URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)

        # Extract PDF src attribute from <embed>, <iframe>, or viewer script
        pdf_src = await page.evaluate("""
            () => {
                const embed = document.querySelector("embed[type='application/pdf']");
                if (embed && embed.src.startsWith("data:")) return embed.src;

                const iframe = document.querySelector("iframe");
                if (iframe && iframe.src.startsWith("data:")) return iframe.src;

                // Fallback for PDF viewer script (PDF.js)
                const scripts = [...document.querySelectorAll("script")];
                for (const s of scripts) {
                    if (s.innerHTML.includes("data:application/pdf;base64")) {
                        const match = s.innerHTML.match(/data:application\\/pdf;base64,[A-Za-z0-9+/=]+/);
                        if (match) return match[0];
                    }
                }
                return null;
            }
        """)

        if not pdf_src:
            logger.error("No embedded data: PDF found on page")
            raise Exception("No PDF found")

        # Extract base64 part
        base64_data = pdf_src.split(",")[1]
        pdf_bytes = base64.b64decode(base64_data)

        # Generate a filename based on URL or timestamp
        filename = url.split("/")[-1].replace(".html", "").replace(".php", "")
        if not filename:
            filename = "downloaded_file"

        pdf_path = DOWNLOAD_DIR / f"{filename}.pdf"

        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"PDF extracted and saved: {pdf_path.name}")

        await browser.close()
        return pdf_path
