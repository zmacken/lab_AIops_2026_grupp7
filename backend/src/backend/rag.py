from pydantic_ai import Agent
from backend.data_models import RagResponse
from backend.constants import VECTOR_DATABASE_PATH
import lancedb
from backend.model import nvidia_model

vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)

rag_agent = Agent(
    model=nvidia_model(),
    retries=2,
    instructions=(
        # TODO: Lägg till instruktioner för agenten här
    ),
    output_type=RagResponse,
)

@rag_agent.tool_plain
def retrieve_top_document(query: str) -> str:
    """
    vector search to match closest document to the query
    """
    results = vector_db["mcf_chunks"].search(query=query).to_list() #byt från articles till rätt name på tabellen som innehåller dina dokument

    return f"""
    
    Filename: {results[0]["filename"]},
    
    Filepath: {results[0]["filepath"]},

    Content: {results[0]["content"]}
    
    """