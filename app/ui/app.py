import requests
import streamlit as st

API_URL = "http://localhost:8000/chat"

st.set_page_config(
    page_title="BravoBot",
    page_icon="💬",
)

st.title("💬 BravoBot")

# historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# mostrar historial
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
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

    with st.chat_message("user"):
        st.markdown(prompt)

    # respuesta bot
    with st.chat_message("assistant"):

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