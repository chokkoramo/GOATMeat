import requests
import streamlit as st

API_URL = "http://localhost:8000/chat"

st.set_page_config(
    page_title="BravoBot",
    page_icon="🐐",
)

st.markdown("""
<style>

/* Fondo general */
body {
    background-color: #f5f5f5;
}
            
<div style="
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
">
    <img src="app/ui/assets/logo.png" 
         style="width:55px; height:55px; object-fit:contain;">
    <h1 style="
        margin:0;
        color:#4B2E83;
        font-size:42px;
    "/>
</div>

/* Header */
h1 {
    color: #4B2E83; /* morado institucional */
    text-align: center;
}
            
/* Caja del chat */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 10px;
}        

/* Mensaje usuario */
[data-testid="stChatMessage"][data-testid*="user"] {
    background-color: #EDE7F6; /* morado claro */
}

/* Mensaje bot */
[data-testid="stChatMessage"][data-testid*="assistant"] {
    background-color: #FFFFFF;
    border: 1px solid #DDD;
}


/* Botón (por si aparece alguno) */
button {
    background-color: #4B2E83 !important;
    color: white !important;
    border-radius: 8px !important;
}
            


/* Spinner */
[data-testid="stSpinner"] {
    color: #4B2E83 !important;
}
            



</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 5])

with col1:
    st.image("app/ui/assets/logo.png", width=100)

with col2:
    st.markdown(
        "<h1 style='margin-bottom:0;'>BravoBot</h1>",
        unsafe_allow_html=True
    )

# historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# Diccionario para mapear los avatares según el rol
avatars = {
    "user": "👤",
    "assistant": "👾"
}

# mostrar historial
for message in st.session_state.messages:
    # Obtenemos el avatar correcto usando el rol ("user" o "assistant")
    current_avatar = avatars.get(message["role"])
    
    with st.chat_message(message["role"], avatar=current_avatar):
        st.markdown(message["content"])


# input tipo chatbot
if prompt := st.chat_input("Escribe tu pregunta"):

    # mostrar mensaje usuario
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # respuesta bot
    with st.chat_message("assistant", avatar="👾"):

        with st.spinner("Pensando..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "question": prompt
                    },
                    timeout=60
                )

                # DEBUG visible
                print("Status:", response.status_code)
                print("Response:", response.text)

                if response.status_code != 200:

                    error_msg = f"Error API: {response.status_code}"

                    st.error(error_msg)

                    st.text(response.text)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_msg
                        }
                    )

                else:

                    data = response.json()

                    answer = data["answer"]

                    st.markdown(answer)

                    # mostrar fuentes
                    if data.get("sources"):

                        st.markdown("**Fuentes:**")

                        for url in data["sources"]:
                            st.markdown(f"- {url}")

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

            except requests.exceptions.ConnectionError:

                msg = "No se pudo conectar con la API"

                st.error(msg)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": msg
                    }
                )

            except requests.exceptions.JSONDecodeError:

                msg = "La API no devolvió JSON"

                st.error(msg)

                st.text(response.text)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": msg
                    }
                )