from flask import Flask, request, jsonify
from flask_cors import CORS
from prompt import SYSTEM_PROMPT

# Funcion de busqueda desde el retriever
# from retriever.vector_store import 

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pregunta_usuario = data.get('message', '')

    if not pregunta_usuario:
            return jsonify({"error": "No message provided"}), 400

        # 1. PASO CLAVE: Obtener contexto de la base de datos vectorial
        # (Este paso lo coordinas con la Persona 2)
        # contexto = buscar_en_db(pregunta_usuario)
    contexto = "Aquí irá el texto que encuentre el scraper..." # Mock temporal

        # 2. Enviar al LLM (Ejemplo usando LangChain + Ollama/Llama3)
        # Aquí es donde ocurre la magia del RAG
    respuesta_ia = f"Respuesta generada usando el contexto: {contexto}" # Simulación

    return jsonify({
            "response": respuesta_ia,
            "sources": ["Página oficial Pascual Bravo"] # Para transparencia
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)