from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

# FastAPI application instance
app = FastAPI()

# --- CORS so that the frontend (file:// or localhost) can call the API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # in production you would restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Chroma persistent database
client = chromadb.PersistentClient(path="chroma")

# Embedding function (OpenAI)
embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("CHROMA_OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Load existing collection created by ingest.py
collection = client.get_collection(
    name="quotes",
    embedding_function=embedding_fn
)


class QueryRequest(BaseModel):
    query: str


@app.post("/search")
def search_quotes(req: QueryRequest):
    """Return most relevant quotes using vector similarity."""
    results = collection.query(
        query_texts=[req.query],
        n_results=3
    )

    output = []
    for i in range(len(results["documents"][0])):
        output.append({
            "quote": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": results["distances"][0][i],
        })

    return {"results": output}
