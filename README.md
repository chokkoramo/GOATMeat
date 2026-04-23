# GOATMeat

# BravoBot

Asistente inteligente basado en IA diseñado para responder preguntas sobre la Institución Universitaria Pascual Bravo, utilizando exclusivamente información oficial.

---

## Descripción

Cada semestre, cientos de aspirantes buscan información detallada sobre la oferta académica, procesos de admisión, requisitos, costos y beneficios de estudiar en la Institución Universitaria Pascual Bravo.

Navegar por un sitio web institucional para encontrar información específica puede ser lento y frustrante.

**BravoBot** surge como una solución a este problema:  
un asistente inteligente disponible capaz de responder preguntas en segundos, utilizando únicamente información verificada.

---

## ¿Para quién es?

- Aspirantes a la institución
- Estudiantes actuales
- Personas interesadas en programas académicos

---

## ¿Qué hace?

- Responde preguntas sobre programas académicos
- Proporciona información específica (ej: duración, semestres)
- Usa únicamente información oficial
- Incluye fuentes cuando están disponibles

---

## Ejemplos de uso

- ¿Cuántos semestres tiene Ingeniería de Software?
- ¿Qué ingenierias puedo ver en la institución?

---

## Tecnologías utilizadas

- **FastAPI** → Backend API
- **Streamlit** → Interfaz de usuario
- **LangChain** → Orquestación del flujo RAG
- **ChromaDB** → Base de datos vectorial
- **Ollama (Llama3:8B)** → Modelo de lenguaje local
- **HuggingFace Embeddings** → Vectorización de texto
- **Docker** → Contenerización

---

## Arquitectura

El sistema sigue un enfoque **RAG (Retrieval-Augmented Generation)**:

1. El usuario escribe una pregunta en la interfaz (Streamlit)
2. La pregunta se envía al backend (FastAPI)
3. Se consulta la base de datos vectorial (ChromaDB)
4. Se recupera el contexto relevante
5. El modelo LLM (Llama3 con Ollama) genera la respuesta
6. Se devuelve la respuesta junto con sus fuentes

---

## Instalación y ejecución

### Requisitos

- Docker
- Docker Compose
- Ollama instalado (solo para ejecución local)

---

### Pasos

1. Clonar el repositorio:

```bash
git clone <tu-repo>
cd <tu-repo>
```

2. Descargar el modelo:
   
```bash
ollama pull llama3:8b
```

3. Ejecutar el proyecto:
```bash
docker compose up --build
```

---

### Acceso

Frontend: http://localhost:8501

API: http://localhost:8000

---

### Interfaz


<img width="1918" height="915" alt="Captura de pantalla 2026-04-23 024159" src="https://github.com/user-attachments/assets/7d712767-5b67-437f-a590-99d4dd633abb" />

---

<img width="1918" height="917" alt="Captura de pantalla 2026-04-23 024219" src="https://github.com/user-attachments/assets/ae7ed91d-f824-4a06-8548-8ce3996ea18d" />

---

### Autores
- Juan Camilo Perdomo

- Jhorman Alejandro Cadavid

- Santiago Cárdenas

- Thomas Grisales





