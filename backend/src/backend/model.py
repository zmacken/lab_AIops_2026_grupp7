from pydantic import BaseModel, Field

class Prompt(BaseModel):
    prompt: str=Field(min_length=1, description="Fråga om krisberedskap")

class Source(BaseModel):
    title: str=Field(description="Sidans titel på mcf.se")
    url: str=Field(description="Sidans URL på mcf.se")

class RagResponse(BaseModel):
    answer: str=Field(description="Svaret på frågan")
    sources: list[Source]=Field(description="Lista med källor")
