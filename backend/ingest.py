import os
import json
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
load_dotenv()

#this file ingests a dataset of quotes into a ChromaDB vector database
# each quote is embedded using an OpenAI embedding model
# and stored in a collection along with metadata (author, category) for retrieval
# after ingestion, the collection can be queried for similar quotes based on text input


JSON_PATH = "data/quotes.json"   # Path to the dataset
COLLECTION_NAME = "quotes"       # Collection name for ChromaDB


def load_quotes(path: str):
    """
    Loads the JSON file and extracts documents, metadata, and unique IDs.
    Each quote becomes a retrievable cluster in the vector database.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)  # Expecting a list of quote objects

    docs = []
    metadatas = []
    ids = []

    for i, item in enumerate(data):
        quote = item.get("Quote")
        author = item.get("Author")
        category = item.get("Category")

        if not isinstance(quote, str):
            continue

        # Final text inserted into embeddings
        if isinstance(author, str):
            text = f'"{quote}" — {author}'
        else:
            text = quote

        text = text.replace("\n", " ")

        docs.append(text)
        metadatas.append({
            "author": author,
            "category": category,
        })
        ids.append(f"quote_{i}")

    return docs, metadatas, ids


def main():
    """
    1. Connect to a local ChromaDB persistent client.
    2. Define an embedding function using an OpenAI embedding model.
       The model maps each document to a high-dimensional numerical vector.
    3. Create (or load) a collection that stores those vectors and their metadata.
    4. Load the quotes dataset and insert all quotes into the collection.

    After this step, the collection can be queried with a new text query: the
    query is embedded into the same vector space, and nearest-neighbor search
    retrieves the most semantically similar quotes.

    """
    # Connect to local ChromaDB 
    client = chromadb.PersistentClient(path="chroma")

    # Define embedding function using OpenAI
    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("CHROMA_OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )

    # Create or get collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    # Load quotes from JSON file
    docs, metas, ids = load_quotes(JSON_PATH)

    # Clear existing data in the collection
    if collection.count() > 0:
        collection.delete(ids=collection.get()["ids"])

    # Insert into vector database
    collection.add(
        documents=docs,
        metadatas=metas,
        ids=ids
    )

    print(f"Ingested {len(docs)} quotes into Chroma collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()
