# 📄 Chandra-OCR Automation Pipeline - Playwright

This project automates the full workflow of:

1. Reading an **Excel file** containing invoice links
2. Opening each link using **Playwright**
3. Detecting whether the link is:
   * A **normal URL** (HTTP/HTTPS)
   * Or a **Base64-encoded Data URL**
4. Downloading the **PDF file**
5. Sending the PDF to the **Marker OCR API**
6. Saving the extracted **Markdown output** using the **same file name**

---

## 🚀 Features

* ✔ Supports **HTTP/HTTPS PDF download**
* ✔ Supports **Base64 Data URL PDFs**
* ✔ Extracts **PDF name automatically**
* ✔ Saves results in `markdown_output/` with **same base name**
* ✔ 100% configurable and extensible

---

## 📁 Project Structure

```
project/
│
├── main.py
├── downloader.py
├── config.py
├── logger.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Create virtual environment

```bash
python -m venv env
source env/bin/activate   # Linux/Mac
env\Scripts\activate      # Windows
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Install Playwright browsers

```bash
playwright install
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```
CHANDRA_API_KEY=your_api_key_here

CHANDRA_URL="https://www.datalab.to/api/v1/marker"

# Folders
DOWNLOAD_DIR=downloads
OUTPUT_DIR=markdown_output

# Excel input
EXCEL_PATH=links.xlsx

```

---

## 📘 Excel Format

Your XLSX file **must contain a column** named exactly:

```
Final Invoice Link
```
---

## ▶️ Running the Project

Simply execute:

```bash
python main.py
```

The pipeline will:

* Read Excel
* Download each PDF
* Send to OCR
* Save output markdown files

---

## 📦 Output

### 📁 Downloaded PDFs

Saved to:

```
downloads/
```

### 📝 OCR Markdown Output

Saved to:

```
markdown_output/<same-name-as-pdf>.md
```

Example:

```
invoice123.pdf → invoice123.md
```

---

## 🧰 Logging

All logs automatically saved to:

```
logs/app.log
```

Log levels include:

* INFO: Process steps
* ERROR: OCR failures or download issues
