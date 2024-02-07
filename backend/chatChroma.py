from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import chromadb
import os
import openai
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA

author_repoName = input("Enter the name of the existing collection (e.g., pinecone): ")

if os.getenv("OPENAI_API_KEY") is not None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print ("OPENAI_API_KEY is ready")
else:
    print ("OPENAI_API_KEY environment variable not found")

EMBEDDING_MODEL = "text-embedding-3-small"
client = chromadb.PersistentClient(path="db")
print(client.list_collections())
collection = client.get_collection(author_repoName)

embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=EMBEDDING_MODEL)

persist_directory = 'db'
embedding = OpenAIEmbeddings(disallowed_special=())

# ------- Now we can use the vectordb to query the documents
# load the persisted database from disk, and use it as normal. 
print("Loading...")
vectordb = Chroma(persist_directory=persist_directory, 
                  embedding_function=embedding,
                  collection_name=author_repoName,
                  )

print("Retrieving...")
retriever = vectordb.as_retriever(search_kwargs={"k": 4})

# create the chain to answer questions 
qa_chain = RetrievalQA.from_chain_type(
                                llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, streaming=True, verbose=True), 
                                chain_type="stuff", 
                                retriever=retriever, 
                                return_source_documents=True,)

## Cite sources
def process_llm_response(llm_response):
    print(llm_response['result'])
    print('\n\nSources:')
    for source in llm_response["source_documents"]:
        print(source.metadata['source'])

while True:
    query = input("Question: ")
    if query.strip() == "":
        continue
    res = qa_chain.invoke(query)    
    process_llm_response(res)
