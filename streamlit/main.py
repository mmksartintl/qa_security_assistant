import os
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv("GROP_API_KEY")
model_name = os.getenv("MODEL_NAME")

from langchain_groq import ChatGroq

llm = ChatGroq(temperature=0.5,groq_api_key=groq_api_key,
               model_name=model_name)

from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

embeddings = HuggingFaceEmbeddings()

def create_vector_db():
    loader = CSVLoader(file_path='seguranca_faq.csv', source_column='prompt')
    data = loader.load()
    vectordb = FAISS.from_documents(documents=data, embedding=embeddings)
    vectordb.save_local("faiss_indx_db")

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA 

def get_qa_chain():
    vectordb1 = FAISS.load_local("faiss_indx_db", embeddings, allow_dangerous_deserialization=True)
    retriever = vectordb1.as_retriever()

    prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

CONTEXT: {context}

QUESTION: {question}

ANSWER:
"""

    PROMPT = PromptTemplate(
       template=prompt_template, input_variables=["context", "question"]
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        input_key="query",
        return_source_documents=True,
        chain_type_kwargs = {"prompt": PROMPT}
    )
    print("exit get_qa_chain")
    return chain

import streamlit as st
# from langchain_helper import create_vector_db

st.title("Help Chat")
load_button = st.button("Load QA")

print("load pressed")
create_vector_db()
qa_chain = get_qa_chain()
print("exit load")
    
prompt_question = st.text_input("Enter the question :")
submit_button = st.button("Submit")

if submit_button:

    res = qa_chain(prompt_question)

    st.code(res["result"], wrap_lines=True)
