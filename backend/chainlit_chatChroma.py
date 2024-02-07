from typing import List
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_community.document_loaders import (
    PyMuPDFLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain.indexes import SQLRecordManager, index
from langchain.schema import Document
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableConfig
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Optional
from src.github_utils import get_repos

import chainlit as cl

persist_directory = 'db'
embedding = OpenAIEmbeddings(disallowed_special=())
# author_repoName = input("Enter the name of the existing collection (e.g., pinecone): ")
author_repoName = "canopy" 


model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)
vectordb = Chroma(persist_directory=persist_directory, 
                  embedding_function=embedding,
                  collection_name=author_repoName,
                  )

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
async def on_chat_start():
    app_user = cl.user_session.get("user")
    print(app_user)
    repos_url = app_user.metadata['raw_user_data']['repos_url']
    access_token = app_user.metadata['token']
    repos = get_repos(repos_url, access_token)
    
    print("\nRepos available:")
    for repo in repos:
        print(repo['name'])
        
    template = """You are a knowledgeable coding assistant that has access to the contents of a repository. You can help me answer questions about the repository. Here is the context of the repository:

    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    retriever = vectordb.as_retriever()

    runnable = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable
    msg = cl.Message(content="")

    class PostMessageHandler(BaseCallbackHandler):
        """
        Callback handler for handling the retriever and LLM processes.
        Used to post the sources of the retrieved documents as a Chainlit element.
        """

        def __init__(self, msg: cl.Message):
            BaseCallbackHandler.__init__(self)
            self.msg = msg
            self.sources = set()  # To store unique pairs

        def on_retriever_end(self, documents, *, run_id, parent_run_id, **kwargs):
            for d in documents:
                source_page_pair = (d.metadata['source'], d.metadata['page'])
                self.sources.add(source_page_pair)  # Add unique pairs to the set

        def on_llm_end(self, response, *, run_id, parent_run_id, **kwargs):
            if len(self.sources):
                sources_text = "\n".join([f"{source}#page={page}" for source, page in self.sources])
                self.msg.elements.append(
                    cl.Text(name="Sources", content=sources_text, display="inline")
                )

    async with cl.Step(type="run", name="AskGit", show_input="true"):
        async for chunk in runnable.astream(
            message.content,
            config=RunnableConfig(callbacks=[
                cl.LangchainCallbackHandler(),
                PostMessageHandler(msg)
            ]),
        ):
            await msg.stream_token(chunk)

    await msg.send()
