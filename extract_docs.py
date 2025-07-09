# extract_docs.py
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredWordDocumentLoader, TextLoader

DOC_DIR = Path("documents")

def load_directory() -> list:
    docs = []
    for file in DOC_DIR.iterdir():
        if file.suffix.lower() == ".pdf":
            docs.extend(PyMuPDFLoader(str(file)).load())     # fast PDF parsing:contentReference[oaicite:5]{index=5}
        elif file.suffix.lower() in {".docx", ".doc"}:
            docs.extend(UnstructuredWordDocumentLoader(str(file)).load())
        else:
            docs.extend(TextLoader(str(file)).load())
    return docs
