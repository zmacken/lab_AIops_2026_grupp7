from pathlib import Path
import os
import cohere

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