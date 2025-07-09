"""
Common RAG · FastAPI interface
Save me next to rag_cli.py
Run with: uvicorn rag_api:app --reload --port 8000
"""
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client

# --- env & globals ---------------------------------------------------------
load_dotenv(".env")                                    # same pattern you already use
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

supabase_client: Optional["SupabaseClient"] = None
vector_store:     Optional[SupabaseVectorStore] = None

# --- FastAPI app -----------------------------------------------------------
app = FastAPI(title="Common RAG API", version="0.1.0")

# (optional) allow front-end calls from anywhere while prototyping
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- models ----------------------------------------------------------------
class ChatRequest(BaseModel):
    query: str
    k: int = 5               # top-k chunks to fetch

class ChatResponse(BaseModel):
    answer: str

# --- lifecycle -------------------------------------------------------------
@app.on_event("startup")
async def startup() -> None:
    """
    Create a single Supabase client & vector store once the app boots.
    """
    global supabase_client, vector_store
    supabase_client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )                                                  # Supabase-py init :contentReference[oaicite:5]{index=5}
    vector_store = SupabaseVectorStore(
        client=supabase_client,
        table_name="common_rag_documents",             # prefix already matches spec
        query_name="common_rag_match_documents",
        embedding=embeddings,
    )

# --- routes ----------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Retrieve context with vector search & answer via OpenAI chat model.
    """
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")

    docs = vector_store.similarity_search(req.query, k=req.k)       # LangChain call :contentReference[oaicite:6]{index=6}
    context = "\n\n".join(d.page_content for d in docs)
    prompt = (
        "Answer in markdown using only the context below.\n\n"  # ← added
        f"{context}\n\nQ: {req.query}\nA:"
    )
    answer = llm.invoke(prompt).content
    return ChatResponse(answer=answer)

# uvicorn rag_api:app --reload --port 8000