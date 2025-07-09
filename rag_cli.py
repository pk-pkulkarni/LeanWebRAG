# rag_cli.py
import os, asyncio
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"),
                         os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

emb = OpenAIEmbeddings()
vs = SupabaseVectorStore(
    client=supabase,
    table_name="common_rag_documents",
    query_name="common_rag_match_documents",
    embedding=emb,
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)                # OpenAI SDK v1 pattern:contentReference[oaicite:9]{index=9}

async def main():
    while True:
        q = input("\nYou:  ")
        if q.lower() in {"exit", "quit"}:
            break
        docs = vs.similarity_search(q, k=5)
        context = "\n\n".join(d.page_content for d in docs)
        prompt = (
            "Answer **in markdown** using only the context below.\n\n"  # ← added
            f"{context}\n\nQ: {q}\nA:"
        )
        print(llm.invoke(prompt).content)

if __name__ == "__main__":
    asyncio.run(main())
