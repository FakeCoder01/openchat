from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader, UnstructuredPDFLoader, OnlinePDFLoader
from django.core.files.storage import FileSystemStorage
import os

from openchat.settings import BASE_DIR


os.environ['OPENAI_API_KEY'] = "API_KEY"
def file_upload_handler(file_url):
    if True:
        print(file_url)
    
        loader = UnstructuredPDFLoader(f"{file_url}")

        documents = loader.load()

        ### delete file
        fs = FileSystemStorage()
        uploaded_file_path = fs.path(file_url)
        fs.delete(uploaded_file_path)

        text_splitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
        documents = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(documents, embeddings)
        retreiver = vectorstore.as_retriever()
        qa = ConversationalRetrievalChain.from_llm(llm = OpenAI(temperature = 0), retriever = retreiver)

        return True
    # except Exception as err:
    #     print(err)
    #     return False
    
