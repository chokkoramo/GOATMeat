from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from app.rag.retriever import ask_question

load_dotenv()

app = FastAPI(
    title="BravoBot API",
    version="1.0"
)


class Question(BaseModel):

    question: str


@app.get("/")
def root():

    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(q: Question):

    result = ask_question(
        q.question
    )

    return result