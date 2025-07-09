# Common RAG – Minimal‑Files Retrieval‑Augmented Generation Stack

This repository is a **compact end‑to‑end RAG template** that

* crawls an entire website with **Crawl4AI** (BFS strategy),
* OCR‑extracts text from images and parses PDFs, Word, Excel, CSV & plain‑text via **LangChain + Unstructured**,
* chunks & embeds all content with **OpenAI** embeddings,
* stores vectors in **Supabase pgvector**, and
* serves answers through both a **CLI** and a **FastAPI + Bootstrap 5 chat UI**.

The same codebase runs on **Windows 11** and **Amazon Linux 2**—only two wheel substitutions and three extra system packages differ.

---

## Folder layout

```
common_rag/
├─ documents/            # PDFs, DOCX, images, spreadsheets, CSVs
│
├─ .env.example          # copy → .env and fill keys
├─ requirements.txt      # Windows dev
├─ requirements_aws.txt  # Amazon Linux prod
│
├─ scrape_site.py        # Crawl4AI deep‑crawl → markdown blob
├─ extract_docs.py       # loaders for every file type
├─ ingest_embeddings.py  # chunk → embed → Supabase upsert
├─ rag_cli.py            # quick REPL
├─ rag_api.py            # FastAPI JSON API
└─ index.html            # Bootstrap 5 chat UI
```

## Architecture

### Ingestion

```
website  ──┐                  ┌── images / PDFs / DOCX / XLSX / CSV
           │                  │
      Crawl4AI (BFS)          │     LangChain + Unstructured loaders
           │                  │
   combined markdown          │   list[Document]
           └─────► concat ────┴────────────────► TextSplitter
                                                 │
                         OpenAI Embeddings (1536‑d)
                                                 │
                                       Supabase pgvector
```

### Retrieval & Serving

* **CLI** (`rag_cli.py`) and **FastAPI** (`rag_api.py`) both call the same LangChain `SupabaseVectorStore` retriever, then pipe context → *GPT‑4o mini*.
* The web UI streams Markdown answers and shows a CSS “typing…” animation.

---

## Setup

### Windows 10 / 11

```bash
git clone <repo>
cd common_rag
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env    # add your keys + SCRAPE_URL
```

No extra OS libs are required—the wheel **`python‑magic‑bin`** bundles `libmagic.dll`.

### Amazon Linux 2

```bash
sudo yum update -y
sudo yum install -y tesseract poppler-utils file-devel   # OCR, PDF & libmagic

git clone <repo> && cd common_rag
python -m venv venv && source venv/bin/activate
pip install -r requirements_aws.txt
cp .env.example .env
```

Linux uses **`python‑magic`** which links against the `libmagic.so` provided by `file-devel`.

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI key |
| `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` | Supabase project creds |
| `SCRAPE_URL` | Root URL to crawl |
| `SCRAPE_MAX_PAGES`, `SCRAPE_MAX_DEPTH` | Optional crawl limits |
| `TESSDATA_PREFIX` | Only if Tesseract is outside default path |

---

## Installation matrix

| OS | Requirements file | Notes |
|----|-------------------|-------|
| **Windows** | `requirements.txt` | uses `python‑magic‑bin`, plain `uvicorn` |
| **Amazon Linux** | `requirements_aws.txt` | uses `python‑magic`, `uvicorn[standard]` |

Both include:

* `unstructured[local-inference]`
* `openpyxl`
* `pymupdf`

---

## Data ingestion workflow

1. Place files in `documents/` or set `SCRAPE_URL`.
2. Run `python ingest_embeddings.py` to crawl/OCR/parse → embed → upsert.
3. Supabase table `common_rag_documents` now holds all vectors.

---

## Running

### CLI

```bash
python rag_cli.py
❓  Do you provide AI solutions?
```

### FastAPI + UI

```bash
uvicorn rag_api:app --host 0.0.0.0 --port 8000
# open index.html via any static server, e.g. python -m http.server 9000
```

---

## Windows vs AWS differences

| Area | Windows | Amazon Linux 2 |
|------|---------|----------------|
| File‑type lib | `python‑magic‑bin` wheel bundles `libmagic.dll`. | `python‑magic` + `file-devel`. |
| OCR | Requires the standard Windows Tesseract installer. | `sudo yum install tesseract`. |
| PDF helper | Poppler is optional. | `poppler-utils` recommended. |
| Uvicorn | `uvicorn` | `uvicorn[standard]` adds uvloop & httptools. |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `TesseractNotFoundError` | Ensure `tesseract -v` works and set `TESSDATA_PREFIX` if needed. |
| `ImportError: failed to find libmagic` | Install `file-devel` then reinstall `python-magic`. |
| Blank answers from images | Use ≥150 dpi images; OCR accuracy falls on low-res graphics. |

---

### References

* Crawl4AI docs · Unstructured loaders · Supabase vector guide · OpenAI embeddings & GPT‑4o mini · uvicorn production tips.
