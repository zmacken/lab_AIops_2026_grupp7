from pathlib import Path

# Läser en Markdown-fil (.md) och returnerar innehållet som text
def read_markdown_file(file_path: str) -> str:
    """Read a Markdown file and return its text content."""
    path = Path(file_path)
    return path.read_text(encoding="utf-8")