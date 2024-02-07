import os
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
import chromadb

os.environ["OPENAI_API_KEY"] = "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"

persist_directory = 'db'
embedding = OpenAIEmbeddings(disallowed_special=())
author_repoName = input("Enter the name of the existing collection (e.g., pinecone): ")

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
