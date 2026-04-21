import streamlit as st

st.set_page_config(page_title="BravoBot - I.U. Pascual Bravo", page_icon="🤖")

st.title("🤖 BravoBot")
st.markdown("Bienvenido al asistente inteligente de la **I.U. Pascual Bravo**. ¿En qué puedo ayudarte hoy?")

# Inicializar el historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe tu duda sobre admisiones, costos o programas..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Respuesta provisional (mientras integran el RAG)
    response = f"Pronto te daré información oficial sobre: {prompt}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})