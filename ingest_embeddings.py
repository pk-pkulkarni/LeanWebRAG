# ingest_embeddings.py
import asyncio
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter   # core splitter pattern:contentReference[oaicite:6]{index=6}
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document
from supabase import create_client
from extract_docs import load_directory
from scrape_site import scrape

## 1. collect raw docs
docs = load_directory()
md = asyncio.run(scrape())
docs.append(Document(page_content=md, metadata={"source": os.getenv("SCRAPE_URL")}))
# website markdown -> single doc

## 2. chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

## 3. embed
emb = OpenAIEmbeddings(model="text-embedding-3-small")              # cheapest, 1536-d
vectors = [emb.embed_query(c.page_content) for c in chunks]

## 4. upsert into Supabase
supabase = create_client(os.getenv("SUPABASE_URL"),
                         os.getenv("SUPABASE_SERVICE_ROLE_KEY"))      # official Python client intro:contentReference[oaicite:7]{index=7}

store = SupabaseVectorStore(
    client=supabase,
    table_name="common_rag_documents",
    query_name="common_rag_match_documents",
    embedding=emb,
)

store.add_texts([c.page_content for c in chunks],
                metadatas=[c.metadata for c in chunks],
                ids=None)                                            # LangChain→Supabase glue:contentReference[oaicite:8]{index=8}
print(f"Upserted {len(chunks)} chunks.")
