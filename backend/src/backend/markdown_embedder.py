import re

import lancedb
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

from backend.constants import TABLE_NAME, VECTOR_DATABASE_PATH

load_dotenv()

embedding_model = get_registry().get("cohere").create(name="embed-multilingual-v3.0")

MAX_CHARS = 1500
MIN_CHARS = 80

SKIP_URLS = {"https://www.mcf.se/sv/rad-till-privatpersoner/"}


class Chunk(LanceModel):
    doc_id: str
    title: str
    url: str
    heading: str
    content: str = embedding_model.SourceField()
    embedding: Vector(embedding_model.ndims()) = embedding_model.VectorField()


def parse_markdown(text: str) -> tuple[dict, str]:
    """Split the file into frontmatter (title, source) and the body text."""
    meta = {}
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
        text = text[match.end() :]
    return meta, text


def clean_markdown(text: str) -> str:
    """Remove boilerplate that appears on every MCF page but is not content."""
    text = text.replace("­", "")  # remove invisible soft hyphens

    lines = []
    skip_toc = False
    for line in text.splitlines():
        if line.startswith("[Till innehåll på sidan]") or line.startswith("[Lyssna]("):
            continue
        if line.strip() == "Visa större bild":
            continue

        if line.strip() == "## På den här sidan":
            skip_toc = True
            continue
        if skip_toc:
            if line.startswith("#"):
                skip_toc = False
            else:
                continue
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)  # remove images ![alt](url)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)  # [text](url) -> text
    text = re.sub(r"\n{3,}", "\n\n", text)  # at most one blank line in a row
    return text.strip()


def split_long_section(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Split a long section at paragraphs (blank lines) so no sentence is cut.
    A paragraph that is too long on its own (e.g. a long bullet list) is split per line."""
    pieces = []
    for paragraph in text.split("\n\n"):
        pieces += paragraph.splitlines() if len(paragraph) > max_chars else [paragraph]

    parts, current = [], ""
    for piece in pieces:
        if current and len(current) + len(piece) > max_chars:
            parts.append(current.strip())
            current = ""
        current += piece + "\n\n"
    if current.strip():
        parts.append(current.strip())
    return parts


def split_into_chunks(text: str, title: str) -> list[dict]:
    """Split the text at every ## heading. Each chunk starts with the page title
    and the heading, so the search knows what the chunk is about."""
    sections = re.split(r"\n(?=## )", "\n" + text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        first_line = section.splitlines()[0]
        heading = (
            first_line.lstrip("#").strip() if first_line.startswith("#") else title
        )

        for part in split_long_section(section):
            if len(part) < MIN_CHARS:
                continue
            content = part if heading == title else f"{title} – {heading}\n\n{part}"
            chunks.append({"heading": heading, "content": content})
    return chunks


def file_to_chunks(file) -> list[dict]:
    """Read a markdown file and return ready-made rows for the Chunk table."""
    meta, body = parse_markdown(file.read_text(encoding="utf-8"))
    url = meta.get("source", "")
    title = meta.get("title", file.stem)
    if not url or url in SKIP_URLS:
        return []

    return [
        {"doc_id": url, "title": title, "url": url, **chunk}
        for chunk in split_into_chunks(clean_markdown(body), title)
    ]


def search_similar_chunks(query: str, limit: int = 3) -> list[dict]:
    """Return the chunks most similar to the query. LanceDB embeds the query
    automatically with the same Cohere model that was used during ingestion."""
    vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)
    table = vector_db[TABLE_NAME]
    return table.search(query).limit(limit).to_list()