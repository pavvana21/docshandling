import azure.functions as func
import logging

from azure.storage.blob import BlobServiceClient, BlobClient, BlobLeaseClient
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain.document_loaders import AzureBlobStorageFileLoader, UnstructuredFileLoader
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="pdfs",
                               connection="BlobStorageConnectionString") 

def blob_trigger_function(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    
    
    blob_name = myblob.name.split("/")[-1]
    
    loader = AzureBlobStorageFileLoader(
    conn_str="DefaultEndpointsProtocol=https;AccountName=cccstorageacc;AccountKey=0GHjbPTEdN175Ze5HX9ZKodMNl3o3uAinCG94Gevwtowu+HMRsN6Kmi/uupWlbIKOGeuOeL/1Mke+AStcO9k5Q==;EndpointSuffix=core.windows.net",
    container="pdfs",
    blob_name=blob_name,
    )

    doc = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_data = text_splitter.split_documents(doc)
    
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store_address: str = "https://cccsearch.search.windows.net"
    vector_store_password: str = "YffQ4ojYwtdJLtRGmioN7I7IklSUWrZDibEYNYhILhAzSeBMMYZS"

    #Create embeddings and vector store instances
    vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name='pdfindex',
    embedding_function=embeddings.embed_query,
    )

    #Insert text and embeddings into vector store
    vector_store.add_documents(documents=split_data)
    