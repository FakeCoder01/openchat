from langchain.llms import OpenAI
import os, openai, faiss, langchain
from gpt_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper 

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, UnstructuredPDFLoader, OnlinePDFLoader


os.environ['OPENAI_API_KEY'] = "API_KEY"


def file_and_conversation(user_id):
    try:
        file_url = f"media/pdf/{user_id}.pdf"
        save_directory = f"faiss-data/{user_id}/"

        loader = UnstructuredPDFLoader(file_url)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
        documents = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vectordb = FAISS.from_documents(documents, embeddings)

        vectordb.save_local(save_directory)
        os.remove(file_url)
        return True
    except Exception as err:
        print(err)
        return False