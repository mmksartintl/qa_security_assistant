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
If you don't know the answer, just say to contact an specialist, don't try to make up an answer.
Provide de answer in Portuguese.

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

create_vector_db()
qa_chain = get_qa_chain()


import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)

#@app.route('/')
#def hello():
    #return 'Hello, World!'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts WHERE id > 1 ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/create', methods=('GET', 'POST'))
def create():
    # if the user clicked on Submit, it sends post request
    if request.method == 'POST':
        # Get the title and save it in a variable
        title = request.form['title']
        # Get the content the user wrote and save it in a variable
        #content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            res = qa_chain(title)
            content = res["result"]
            # Open a connection to databse
            conn = get_db_connection()
            # Insert the new values in the db
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',(title, content))
            conn.commit()
            conn.close()
            # Redirect the user to index page
            return redirect(url_for('index'))

    return render_template('create.html')

