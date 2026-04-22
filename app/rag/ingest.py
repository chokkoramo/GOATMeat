import os
import json
from glob import glob
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

DATA_PATH = "app/scraper/data"
VECTORSTORE_PATH = "app/vectorstore"


def load_documents():
    """
    Carga todos los archivos JSON generados por el scraper
    y los convierte en documentos para el sistema RAG.
    """

    documents = []

    json_files = glob(f"{DATA_PATH}/*.json")

    print(f"Archivos encontrados: {len(json_files)}")

    for file in json_files:

        try:
            with open(file, "r", encoding="utf-8") as f:

                data = json.load(f)

                content = data.get("contenido", "")

                if not content:
                    continue

                metadata = {
                    "titulo": data.get("titulo"),
                    "tipo": data.get("tipo"),
                    "url": data.get("url_origen")
                }

                doc = Document(
                    page_content=content,
                    metadata=metadata
                )

                documents.append(doc)

        except Exception as e:

            print(f"Error leyendo archivo {file}: {e}")

    print(f"Documentos cargados: {len(documents)}")

    return documents


def split_documents(documents):
    """
    Divide los documentos en fragmentos (chunks)
    para mejorar la búsqueda semántica.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    print(f"Chunks generados: {len(chunks)}")

    return chunks


def create_vectorstore(chunks):
    """
    Crea la base vectorial usando embeddings locales.
    """

    print("Cargando modelo de embeddings...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creando vectorstore...")

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH
    )

    print("Vectorstore creado correctamente")


def run_ingest():
    """
    Pipeline completo de ingestión.
    """

    print("\n--- INICIO INGESTA ---")

    docs = load_documents()

    if not docs:
        print("No hay documentos para procesar")
        return

    chunks = split_documents(docs)

    create_vectorstore(chunks)

    print("\n--- INGESTA COMPLETADA ---")


if __name__ == "__main__":

    os.makedirs(VECTORSTORE_PATH, exist_ok=True)

    run_ingest()