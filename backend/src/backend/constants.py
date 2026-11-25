from pathlib import Path

# Constants for the backend application
DATA_PATH = Path(__file__).parents[1] / "data"
VECTOR_DATABASE_PATH = Path(__file__).parents[1] / "knowledge_base"
TABLE_NAME = "mcf_chunks"

# Ensure the data and vector database directories exist
if __name__ == "__main__":
    print(DATA_PATH)
    print(VECTOR_DATABASE_PATH)