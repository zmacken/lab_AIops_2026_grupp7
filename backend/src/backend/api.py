from fastapi import FastAPI                                  
from backend.model import Prompt, RagResponse, Source  

app = FastAPI()

#First endpoint, check if the server is running
@app.get("/test")
async def health():
    return {"status": "ok"}

# 4.Second endpoint, 
@app.post("/chat")
async def chat(query: Prompt) -> RagResponse:

    return RagResponse(
        answer=f"(Testsvar - boten är ej kopplad ännu. Frågan var: {query.prompt})",
        sources=[
            Source(
                title="Hemberedskap – preppa för en vecka",
                url="https://www.mcf.se/sv/rad-till-privatpersoner/hemberedskap---preppa-for-en-vecka/",
            )
        ],
    )