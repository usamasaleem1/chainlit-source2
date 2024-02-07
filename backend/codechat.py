import asyncio
import os
import subprocess
from typing import List
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.docstore.document import Document
from pinecone import Pinecone
import chainlit as cl
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
from chainlit.input_widget import TextInput

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
import subprocess

app = FastAPI()


@app.post("/ingest/")
async def ingest_repo(github_url: str = Form(...)):
    try:
        # Assuming ingest.py accepts a GitHub URL as a command-line argument
        process = subprocess.run(['python', 'ingest.py', github_url], check=True, capture_output=True, text=True)
        return {"message": "Ingestion successful", "output": process.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e.stderr}")


Pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment=os.environ.get("PINECONE_ENV"),
)

index_name = "canopy--askgit"
# namespace = "pinecone-index-76b52b8"
namespace = None
embeddings = OpenAIEmbeddings()

welcome_message = "Ask anything code related about your repo."

# We will cache the response if it is the same as a previous one to increase speed and reduce cost to API
set_llm_cache(InMemoryCache())


def run_test():
    try:
        # Run test.py using the subprocess module
        result = subprocess.run(
            ['python3', 'ingest_inline.py'], check=True)
        print(f"done: {result}")
    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the execution of test.py
        print(f"Error: {e}")


@cl.action_callback("Process")
async def on_action(action: cl.Action):
    run_test()


@cl.on_chat_start
async def start():
    # await cl.Message(content=welcome_message).send()
    docsearch = Pinecone.from_existing_index(
        index_name=index_name, embedding=embeddings, namespace=namespace
    )
    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.1,
            streaming=True,
            verbose=True,
            cache=True,
        ),
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_type="mmr", fetch_k=5),
        memory=memory,
        return_source_documents=True,
    )
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain
    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()

#  Document(page_content='/Uh+Plc5ar6Vp2zOz8QqMifzyQuiQph9nAzspNIWm2/ZyaMyThbSFViI/wQdLfpESO88GnPIkpiLejaml38RpQjJATI3uzYwotsZnxwXwLlZ6KA3/gPGekrHyNr/0aGxuJ8BMhejheTRFVLqsAJjMK6ZIr8+BPOjVtcIj0JW5z4qF5dW1styNu+n2ynHclMP1wH6RO+LSjsGm1lw+74xrhhXcLnZ3EPQwlQ3KW67iUXnImj9BVuug3j2pK+eMFDM', metadata={'document_id': 'frontend_public_awaazo_bird_aihelper_reply_icon.txt', 'source': ''}), Document(page_content='return podcastResponses;\n    }', metadata={'document_id': 'Backend_Backend_Services_PodcastService.txt', 'source': ''}), Document(page_content='Pull Request #135: Added playlist backend api routes #26\nCreated by: shadijiha\nState: closed\nURL: https://github.com/awaazo/awaazo/pull/135', metadata={'document_id': 'pulls.txt', 'source': ''})]
