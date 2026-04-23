import os

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama

from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA


VECTORSTORE_PATH = "app/vectorstore"

def get_retriever():

    print("Cargando embeddings...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Conectando a Chroma...")

    db = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings
    )

    retriever = db.as_retriever(
        search_kwargs={
            "k": 6
        }
    )

    return retriever


def get_qa_chain():

    retriever = get_retriever()

    prompt_template = """
Tu eres BravoBOT, un asistente de inteligencia artificial diseñado para ayudar a los usuarios encontrando informacion relevante sobre la web de la institucion
(Institucion Universitaria Pascual Bravo).

Tu tarea es responder a las preguntas que realizan los usuarios.

REGLAS CRÍTICAS:

1. Usa EXCLUSIVAMENTE el contexto proporcionado para responder.
2. Si la respuesta no está en el contexto, di amablemente:
   "Lo siento, no tengo esa información específica. Te sugiero contactar a admisiones al correo admisiones@pascualbravo.edu.co".
3. Mantén un tono institucional, amable y profesional.
4. No inventes fechas, costos o informacion sobre programas si no aparecen en el texto.
5. Si el usuario pregunta por programas académicos, responde con la informacion sobre dicho programa segun el contexto.
6. Responde siempre en español.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    print("Cargando modelo LLM...")

    llm = Ollama(
        model="llama3:8b",
        temperature=0,
        base_url="http://host.docker.internal:11434"
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PROMPT
        }
    )

    return qa

def ask_question(question: str):

    print("Pregunta:", question)

    qa = get_qa_chain()

    response = qa.invoke(
        {
            "query": question
        }
    )

    answer = response["result"]

    sources = []

    for doc in response["source_documents"]:

        url = doc.metadata.get("url")

        if url:
            sources.append(url)

    return {
        "answer": answer,
        "sources": list(set(sources))
    }