import os
import re
from urllib.parse import urlparse

from dotenv import load_dotenv
from firecrawl import Firecrawl
from firecrawl.v2.types import ScrapeOptions

# Läs in miljövariabler från .env
load_dotenv()

app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Hämta bara huvudinnehållet som markdown (utan meny och sidfot)
scrape_opts = ScrapeOptions(
    only_main_content=True,
    max_age=172800000,  # Använd cache om sidan är yngre än 48 timmar
    parsers=["pdf"],
    formats=["markdown"],
)

crawl_result = app.crawl(
    "https://www.mcf.se/sv/rad-till-privatpersoner/",
    sitemap="include",
    crawl_entire_domain=False,
    scrape_options=scrape_opts,
)

# Skapa mappen "data" om den inte finns
os.makedirs("data", exist_ok=True)


def make_filename(url: str, index: int) -> str:
    """Gör ett filnamn av URL:ens path, t.ex. '01_rad-till-privatpersoner_krisberedskap.md'."""
    path = urlparse(url).path.strip("/").replace("/", "_")
    # Ta bort tecken som inte är tillåtna i filnamn
    path = re.sub(r"[^a-zA-Z0-9_\-åäöÅÄÖ]", "", path)
    return f"{index:02d}_{path or 'index'}.md"


for i, page in enumerate(crawl_result.data, start=1):
    markdown = page.markdown
    # Hoppa över sidor utan innehåll
    if not markdown:
        continue

    metadata = page.metadata
    # Metadatafälten skiljer sig lite mellan versioner, så vi provar flera
    url = getattr(metadata, "source_url", None) or getattr(metadata, "url", None) or f"sida-{i}"
    title = getattr(metadata, "title", None) or url

    filepath = os.path.join("data", make_filename(url, i))

    with open(filepath, "w", encoding="utf-8") as f:
        # Frontmatter med källa så du vet var texten kommer ifrån
        f.write(f"---\ntitle: {title}\nsource: {url}\n---\n\n")
        f.write(markdown)

    print(f"Sparade {filepath}")