import streamlit as st
from agent import agent

st.title("🎬 Movie Ai chat bot")


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("What is up?"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        ai_response = agent.run_sync(prompt)
        response = st.markdown(ai_response.data)
        st.session_state.messages.append({"role": "assistant", "content": ai_response.data})
