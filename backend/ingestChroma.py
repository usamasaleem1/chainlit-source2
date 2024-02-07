import os
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader

os.environ["OPENAI_API_KEY"] = "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"
# Load and process the text files
loader = DirectoryLoader('./repodata_txt', glob="./*.txt", loader_cls=TextLoader)
# Supplying a persist_directory will store the embeddings on disk
persist_directory = 'db'
author_repoName = input("Enter the name of the collection (e.g., pinecone): ")

documents = loader.load()

#splitting the text into
print("Splitting...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# Embed and store the texts
## here we are using OpenAI embeddings but in future we will swap out to local embeddings
print("Embedding...")
embedding = OpenAIEmbeddings(disallowed_special=())

import time
start_time = time.time()

print("Ingesting...")
vectordb = Chroma.from_documents(documents=texts, 
                                 embedding=embedding,
                                 persist_directory=persist_directory,
                                 collection_name=author_repoName,
                                 )

end_time = time.time()
print(f"Time taken to ingest: {end_time - start_time} seconds")

# # persiste the db to disk
vectordb.persist()
vectordb = None


print("run chatChroma.py to query the database with questions")
