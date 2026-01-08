import streamlit as st
import os

# Librerías de LangChain y Ollama
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

st.set_page_config(page_title="UniBot 🎓", page_icon="🎓")
st.title("🎓 Chatbot UCLV")
st.logo("uclv-black.jpg", size="large")

# --- CARGA Y PROCESAMIENTO DE DATOS (Con Caché para velocidad) ---
@st.cache_resource
def load_and_process_data():
    file_path = "../datos_universidad.txt"
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    embeddings = OllamaEmbeddings(
        base_url="http://localhost:11434",
        model="nomic-embed-text"
    )
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    return vectorstore

vectorstore = load_and_process_data()

@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """Inject context into state messages."""
    last_query = request.state["messages"][-1].text
    retrieved_docs = vectorstore.similarity_search(last_query)

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    #print(context)
    system_message = (
        f"""Eres un asistente útil de la universidad.
        Usa los siguientes fragmentos de contexto recuperado para responder la pregunta.
        Mantén la respuesta concisa y en español.\n\n
        {context}"""
    )
    return system_message

llm = ChatOllama(base_url="http://localhost:11434", model="llama3.2:3b", temperature=0)
agent = create_agent(llm, tools=[], middleware=[prompt_with_context])

if "messages" not in st.session_state:
        st.session_state.messages = []

# Mostrar mensajes del historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if query := st.chat_input("Pregunta algo sobre la universidad..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )
            answer = response["messages"][-1].content
            st.markdown(answer)
    
    # Guardar respuesta
    st.session_state.messages.append({"role": "assistant", "content": answer})