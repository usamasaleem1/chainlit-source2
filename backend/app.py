import asyncio
import os
import subprocess
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.docstore.document import Document
from pinecone import Pinecone, ServerlessSpec, PodSpec
import chainlit as cl
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
from chainlit.input_widget import TextInput
from chainlit.server import app
from fastapi import Request
from fastapi.responses import (
    HTMLResponse,
)
from dotenv import load_dotenv
from typing import Dict, Optional
from src.github_utils import get_repos

load_dotenv()

@app.get("/hello")
def hello(request: Request):
    print(request.headers)
    return HTMLResponse("Hello World")

@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  metadata = default_user.metadata
  metadata["token"] = token
  metadata["raw_user_data"] = raw_user_data
  return cl.User(
    identifier=default_user.identifier, metadata=metadata
  )

@cl.on_chat_start
async def start():

    msg = cl.Message(content="")
    await msg.send()

    app_user = cl.user_session.get("user")
    print(app_user)
    repos_url = app_user.metadata['raw_user_data']['repos_url']
    access_token = app_user.metadata['token']
    repos = get_repos(repos_url, access_token)
    
    actions = []
    for repo in repos:
        action = cl.Action(
            name="name", 
            value=f"{repo['name']}", 
            label=f"{repo['name']} Url: {repo['html_url']}",
            description=f"{repo['description']}",
            collapsed=True
        )
        actions.append(action)
    
    res = await cl.AskActionMessage(
        content="Pick a repo!",
        actions=actions,
        timeout=60*5
    ).send()



@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=message.content).send()
