from pathlib import Path
import os
import cohere
from lancedb.embeddings import get_registry
import lancedb

# Läser en Markdown-fil (.md) och returnerar innehållet som text
def read_markdown_file(file_path: str) -> str:
    """Read a Markdown file and return its text content."""
    path = Path(file_path)
    return path.read_text(encoding="utf-8")


# Skapar en embedding av text med Cohere
def create_embedding(text: str) -> list[float]:
    api_key = os.getenv("COHERE_API_KEY")

    if not api_key:
        raise ValueError("COHERE_API_KEY saknas")

    client = cohere.ClientV2(api_key=api_key)

    response = client.embed(
        texts=[text],
        model="embed-multilingual-v3.0",
        input_type="search_document",
        embedding_types=["float"],
    )

    return response.embeddings.float[0]

# Skapar en Cohere-funktion som kan användas av LanceDB
def get_cohere_embedding_function():
    return get_registry().get("cohere").create(
        name="embed-multilingual-v3.0"
    )

# Delar upp text i mindre delar (chunks)
def split_text_into_chunks(text: str, chunk_size: int = 1000) -> list[str]:
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


# Skapar embeddings för flera chunks
def create_chunk_embeddings(chunks: list[str]) -> list[list[float]]:
    fn = get_cohere_embedding_function()
    return fn.compute_source_embeddings(chunks)


# Läser en Markdown-fil, delar upp texten och skapar embeddings
def process_markdown_file(file_path: str):
    text = read_markdown_file(file_path)
    chunks = split_text_into_chunks(text)
    embeddings = create_chunk_embeddings(chunks)

    return chunks, embeddings


# Spara text-chunks och deras embeddings i LanceDB
# Undvika att lägga till samma text flera gånger

def store_embeddings(chunks: list[str], embeddings: list[list[float]]):

    if len(chunks) != len(embeddings):
        raise ValueError("Antalet chunks och embeddings måste vara samma.")

    db = lancedb.connect("data/lancedb")

    data = [
        {"text": chunk, "vector": embedding}
        for chunk, embedding in zip(chunks, embeddings)
    ]

    if "markdown_chunks" in db.table_names():
        table = db.open_table("markdown_chunks")

        existing_texts = set(
            table.to_arrow().column("text").to_pylist()
        )

        new_data = [
            item for item in data
            if item["text"] not in existing_texts
        ]

        if new_data:
            table.add(new_data)

    else:
        table = db.create_table("markdown_chunks", data=data)

    return table


# Söker efter text-chunks som liknar användarens fråga
def search_similar_chunks(query: str, limit: int = 3):
    db = lancedb.connect("data/lancedb")
    table = db.open_table("markdown_chunks")

    fn = get_cohere_embedding_function()
    query_embedding = fn.compute_query_embeddings(query)[0]

    results = (
        table.search(query_embedding)
        .limit(limit)
        .to_arrow()
    )

    return results

# Läser alla Markdown-filer i en mapp och sparar deras embeddings
def process_markdown_directory(directory_path: str):
    directory = Path(directory_path)
    
    # Mappar som inte ska genomsökas
    ignored_dirs = {".venv", ".git", "node_modules", "__pycache__"}

    markdown_files = [
        path for path in directory.rglob("*.md")
        if not any(
            part in ignored_dirs
            for part in path.relative_to(directory).parts
        )
    ]

    processed_files = 0

    for file_path in markdown_files:
        text = read_markdown_file(str(file_path))

        if not text.strip():
            continue

        chunks = split_text_into_chunks(text)
        embeddings = create_chunk_embeddings(chunks)
        store_embeddings(chunks, embeddings)

        processed_files += 1

    return processed_files