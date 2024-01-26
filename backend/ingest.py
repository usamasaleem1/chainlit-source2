import shutil
import turbopuffer as tpuf
import time
from concurrent.futures import ThreadPoolExecutor
import pinecone as pc
import numpy as np
from typing import List
import uuid
import base64
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
import pinecone
from pdfmerge import pdfmerge
import textwrap
from fpdf import FPDF
from dotenv import load_dotenv
from githubkit import GitHub, TokenAuthStrategy
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
import requests
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import sqlite3
import re
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob
import itertools
from openai import OpenAI
from langchain.vectorstores import Weaviate
from canopy.knowledge_base import KnowledgeBase
from canopy.models.data_models import Document
from canopy_cli.data_loader import load_from_path
from canopy.tokenizer.tokenizer import Tokenizer
from canopy.knowledge_base import list_canopy_indexes
from canopy.knowledge_base.record_encoder.openai import OpenAIRecordEncoder
import os
import uuid
import concurrent.futures
import requests
import numpy as np
from typing import List
from concurrent.futures import as_completed
from dotenv import load_dotenv
import os
import glob
import turbopuffer as tpuf
from git import Repo
import git
import openai
from shutil import rmtree
from pathlib import Path
from subprocess import run


# Load environment variables from .env file
load_dotenv()

os.environ["OPENAI_API_KEY"] = ''

# Get your GitHub API token from the environment variables
github_token = os.getenv("GITHUB_TOKEN")

# Initialize the GitHub client
github = GitHub(TokenAuthStrategy(github_token))
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# Modified download_directory function
def clone_projects(project, branch):
    # Assume PATH is defined elsewhere or replace it with the desired path
    Path = "/Users/usamasaleem/Dev Projects/Chainlit_qa/RepoContents/awaazo_awaazo"
    git.Git(
        Path).clone("git://gitorous.org/git-python/mainline.git")


def download_directory():
    repo_url = input("Enter the repository url: ")
    repo_url = repo_url if repo_url.endswith('.git') else repo_url + '.git'
    target_path = "RepoContents"
    # delete RepoContents folder if it exists
    if os.path.exists(target_path):
        rmtree(target_path)
    print(f"Cloning {repo_url} to {target_path}...")
    repo = Repo.clone_from(repo_url, target_path)
    print(f"SUCCESS: Cloned {repo_url} to {target_path}")
    repo.git.pull()
    print(f"SUCCESS: Pulled {repo_url} to {target_path}")

    # delete data_backup folder if it exists
    data_backup_path = "data_backup"
    if os.path.exists(data_backup_path):
        rmtree(data_backup_path)

    # for each file in RepoContents, copy it to data_backup if the file is readable as a text file, and convert it to a .txt file in the data_backup folder
    for root, dirs, files in os.walk(target_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    continue
                elif is_text_file(file_path):
                    print(f"Copying {file_path} to {data_backup_path}")
                    os.makedirs(data_backup_path, exist_ok=True)
                    shutil.copy(file_path, data_backup_path)
                    print(f"SUCCESS: Copied {file_path} to {data_backup_path}")

                    print(f"Converting {file_path} to {data_backup_path}")

                    text_file_name = file_path + '.txt'

                    safe_file_name = text_file_name.replace('/', '_')
                    output_file_path = os.path.join(
                        data_backup_path, safe_file_name)

                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        with open(file_path, 'r', encoding='utf-8') as original_file:
                            f.write(original_file.read())

                    print(
                        f"SUCCESS: Converted {file_path} to {data_backup_path}")

                    # Remove the original file from the data_backup folder
                    os.remove(os.path.join(data_backup_path, file))
                    print(
                        f"SUCCESS: Removed original file {file} from {data_backup_path}")


def is_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Try reading a small chunk to check if it's a text file
            file.read(100)
        return True
    except UnicodeDecodeError:
        # Raised when the file is not a text file
        return False
    except Exception as e:
        # Handle other exceptions as needed
        print(f"Error: {e}")
        return False


def execute(command):
    run(command, capture_output=True, shell=True, check=True, text=True)

# old version of downloading repo contents
# def download_directory(repo_owner, repo_name, target_path='RepoContents', branch='main', token=github_token):
#     api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
#     headers = {
#         'Authorization': f'token {token}',
#         'Accept': 'application/vnd.github.v3+json',
#     }

#     if len(os.listdir(target_path)) > 0:
#         for file_name in os.listdir(target_path):
#             file_path = os.path.join(target_path, file_name)
#             if os.path.isfile(file_path):
#                 os.remove(file_path)

#     def download_contents(url, path=''):
#         response = requests.get(url, headers=headers, params={'ref': branch})
#         response.raise_for_status()
#         contents = response.json()

#         os.makedirs(target_path, exist_ok=True)

#         for content in contents:
#             if content['type'] == 'file':
#                 # Ignore any images or gifs when downloading
#                 if not content['path'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
#                     print(f"Downloading {content['path']}")
#                     file_response = requests.get(
#                         content['download_url'], headers=headers)
#                     file_response.raise_for_status()

#                     # Save the file content into a text file
#                     file_path = os.path.join(
#                         target_path, content['path'].replace('/', '_'))
#                     with open(file_path, 'w', encoding='utf-8') as file:  # 'w' for text mode
#                         # write the text content of the file
#                         file.write(file_response.text)
#             elif content['type'] == 'dir':
#                 # Recursively call download_contents but do not change the target path
#                 new_api_url = os.path.join(api_url, content['path'])
#                 download_contents(
#                     new_api_url, os.path.join(path, content['path']))

#     # Start the recursive downloading
#     download_contents(api_url)

#     # Create data folder if it doesn't exist already
#     if not os.path.exists('data'):
#         os.makedirs('data')
#     # if data folder is not empty, delete all files in it
#     else:
#         for file_name in os.listdir('data'):
#             file_path = os.path.join('data', file_name)
#             if os.path.isfile(file_path):
#                 os.remove(file_path)

#     repo_to_text(target_path, 'data')


def repo_to_text(repo_path, output_path):
    """
    Converts files in a repository to text files and writes them to the given output directory.
    After conversion, the original file is deleted.

    :param repo_path: Path to the repository directory.
    :param output_path: Path to the output directory where text files will be saved.
    """
    print("\nConverting repository files to text...")
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            text_file_name = os.path.splitext(file)[0] + '.txt'
            safe_file_name = ''.join(
                char for char in text_file_name if char.isalnum() or char in "._-")
            output_file_path = os.path.join(output_path, safe_file_name)

            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Delete the original file after conversion
            os.remove(file_path)

    print(f"SUCCESS: Converted repo contents to txt for ingestion")


def get_issues_and_pulls():
    # Input repository owner and name from the user in one line
    repo_input = input("Enter the repository owner and name (user/reponame): ")

    # Split the input by '/' to separate owner and repo
    owner, repo = repo_input.split('/')

    download_directory(repo_owner=owner, repo_name=repo, token=github_token)

    # Call the GitHub API to get all issues for the repository
    print("Getting issues and pull requests...")
    issues_response = github.rest.issues.list_for_repo(
        owner=owner, repo=repo, state="all")

    # Check if the API request for issues was successful
    if issues_response.status_code != 200:
        print(
            f"Failed to retrieve issues. Status code: {issues_response.status_code}")
        return

    # Call the GitHub API to get all pull requests for the repository
    pulls_response = github.rest.pulls.list(
        owner=owner, repo=repo, state="all")

    # Check if the API request for pull requests was successful
    if pulls_response.status_code != 200:
        print(
            f"Failed to retrieve pull requests. Status code: {pulls_response.status_code}")
        return

    issues = issues_response.parsed_data
    pulls = pulls_response.parsed_data

    # Specify the directory where the files should be saved
    save_directory = "data"

    # Create the directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)

    # Define the full paths to the issues and pulls files
    issues_file_path = os.path.join(save_directory, "issues.txt")
    pulls_file_path = os.path.join(save_directory, "pulls.txt")

    # Write the issues to the issues file
    with open(issues_file_path, "w", encoding="utf-8") as issues_file:
        for issue in issues:
            issues_file.write(f"Issue #{issue.number}: {issue.title}\n")
            issues_file.write(f"Created by: {issue.user.login}\n")
            issues_file.write(f"State: {issue.state}\n")
            issues_file.write(f"URL: {issue.html_url}\n\n")
            # add dates

    # Write the pulls to the pulls file
    with open(pulls_file_path, "w", encoding="utf-8") as pulls_file:
        for pull in pulls:
            pulls_file.write(f"Pull Request #{pull.number}: {pull.title}\n")
            pulls_file.write(f"Created by: {pull.user.login}\n")
            pulls_file.write(f"State: {pull.state}\n")
            pulls_file.write(f"URL: {pull.html_url}\n\n")

    print("Converting issues to database...")
    issues_to_db('data/issues.txt', 'data/issues.db')
    print("Converting pull requests to database...")
    pulls_to_db('data/pulls.txt', 'data/pulls.db')
    ingest()


def issues_to_db(issues_file_path, db_file_path):
    # If a database file already exists, remove it to prevent 'database is locked' errors
    if os.path.exists(db_file_path):
        os.remove(db_file_path)

    # Connect to a new database (this will create the .db file if it does not exist)
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Define the schema for our table
    cursor.execute('''
        CREATE TABLE issues (
            issue_number INTEGER PRIMARY KEY,
            title TEXT,
            created_by TEXT,
            state TEXT,
            url TEXT
        )
    ''')

    # Commit the creation of the table
    conn.commit()

    # Define a function to parse a block of lines of our text file
    def parse_block(block):
        # Use regex to find the different parts of the block
        issue_num = re.search(r'Issue #(\d+):', block)
        title = re.search(r'Issue #\d+: (.+?)\n', block)
        created_by = re.search(r'Created by: ([^\s]+)', block)
        state = re.search(r'State: (\w+)', block)
        url = re.search(r'URL: (.+)$', block)

        # Extract the groups if the search was successful
        return (
            int(issue_num.group(1)) if issue_num else None,
            title.group(1).strip() if title else None,
            created_by.group(1).strip() if created_by else None,
            state.group(1).strip() if state else None,
            url.group(1).strip() if url else None
        )

    # Read the file and parse each block
    with open(issues_file_path, 'r') as file:
        # Read the entire file and split by empty lines to separate each issue record
        content = file.read().strip()
        issues_blocks = content.split('\n\n')

        for block in issues_blocks:
            parsed_data = parse_block(block)

            # Insert the parsed data into the issues table using INSERT OR IGNORE
            if all(parsed_data):
                cursor.execute('''
                    INSERT OR IGNORE INTO issues (issue_number, title, created_by, state, url)
                    VALUES (?, ?, ?, ?, ?)
                ''', parsed_data)

    # Commit the insertions and close the connection
    conn.commit()
    conn.close()

    print(
        f"SUCESSS: {db_file_path} created successfully from {issues_file_path}")


def pulls_to_db(pulls_file_path, db_file_path):
    # If a database file already exists, remove it to prevent 'database is locked' errors
    if os.path.exists(db_file_path):
        os.remove(db_file_path)
    # Connect to a new database (this will create the .db file if it does not exist)
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Define the schema for our table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pulls (
            pull_number INTEGER PRIMARY KEY,
            title TEXT,
            created_by TEXT,
            state TEXT,
            url TEXT
        )
    ''')

    # Commit the creation of the table
    conn.commit()

    # Define a function to parse a chunk of our text file representing one pull request
    def parse_chunk(chunk):
        # Use regex to find the different parts of each pull request details
        pull_num = re.search(r'Pull Request #(\d+):', chunk)
        title = re.search(r'Pull Request #\d+: (.+?)\n', chunk)
        created_by = re.search(r'Created by: ([^\s]+)', chunk)
        state = re.search(r'State: (\w+)', chunk)
        url = re.search(r'URL: (.+)', chunk)

        # Extract the groups if the search was successful
        return (
            int(pull_num.group(1)) if pull_num else None,
            title.group(1).strip() if title else None,
            created_by.group(1).strip() if created_by else None,
            state.group(1).strip() if state else None,
            url.group(1).strip() if url else None
        )

    # Read the file and parse each chunk
    with open(pulls_file_path, 'r') as file:
        # Read the entire file as a single string
        file_content = file.read().strip()
        # Split the content by two newlines, which indicates the end of a pull request record
        chunks = file_content.split('\n\n')

        for chunk in chunks:
            parsed_data = parse_chunk(chunk)

            # Insert the parsed data into the pulls table
            if all(parsed_data):
                cursor.execute('''
                    INSERT INTO pulls (pull_number, title, created_by, state, url)
                    VALUES (?, ?, ?, ?, ?)
                ''', parsed_data)

    # Commit the insertions and close the connection
    conn.commit()
    conn.close()

    print(
        f"SUCCESS: Database {db_file_path} created successfully from {pulls_file_path}")


def convertToPdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')
    print("PDF created. Ingesting...")
    # Delete pulls.txt, metadata.txt, and issues.txt
    issues_file_path = os.path.join("data", "issues.txt")
    pulls_file_path = os.path.join("data", "pulls.txt")
    metadata_file_path = os.path.join("data", "metadata.txt")
    os.remove(issues_file_path)
    os.remove(pulls_file_path)
    os.remove(metadata_file_path)
    # ingest()

# Canopy version


def ingest():
    # Initialize OpenAI and Pinecone
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    os.environ["PINECONE_API_KEY"] = ''
    os.environ["PINECONE_ENVIRONMENT"] = 'us-west1-gcp-free'
    os.environ["OPENAI_API_KEY"] = ''
    index_name = "askgit"

    # Initialize the tokenizer (required before using KnowledgeBase)
    Tokenizer.initialize()
    encoder = OpenAIRecordEncoder(model_name="text-embedding-ada-002")
    batch_size = 100

    # Create a KnowledgeBase instance
    kb = KnowledgeBase(index_name=index_name, record_encoder=encoder)
    if not any(name.endswith(index_name) for name in list_canopy_indexes()):
        kb.create_canopy_index(indexed_fields=["title"])

    docs_folder = '/Users/usamasaleem/Dev Projects/Chainlit_qa/data/'

    print(f"\nConnecting to index...")
    # Connect to the existing Pinecone index
    kb.connect()
    print(f"\nConnected to index {index_name}.")

    # List all text files in the docs folder
    file_paths = [os.path.join(docs_folder, f)
                  for f in os.listdir(docs_folder) if f.endswith('.txt')]

    print(f"\nIngesting metadata and repo code into pinecone...\n")

    import time
    start_time = time.time()
    # Load and upsert documents in batches
    for i in range(0, len(file_paths), batch_size):
        batch_files = file_paths[i:i + batch_size]
        documents = []
        for file_path in batch_files:
            with open(file_path, 'r') as file:
                doc_id = os.path.basename(file_path)
                text = file.read()
                documents.append(Document(id=doc_id, text=text))

        # Upsert the batch of documents
        print(f"Creating embeddings for {len(documents)} documents...")
        kb.upsert(documents, show_progress_bar=True, batch_size=batch_size)
        print(f"Upserted {len(documents)} documents.\n")
    end_time = time.time()
    print(
        f"Time taken to complete: {end_time - start_time} seconds or {(end_time - start_time)/60} minutes")


def deleteIndex():
    os.environ["OPENAI_API_KEY"] = ''
    pinecone.init(api_key='',
                  environment='us-west1-gcp-free')

    index_name = "spark"
    index = pinecone.Index(index_name=index_name)
    index.delete(deleteAll=True)


# choose a repo, download and ingest:
# get_issues_and_pulls()

# ingest only, if your data is already in the data folder:
# ingest()

# delete your index for debug purpose:
# deleteIndex()

# only download repo contents:
# download_directory()
