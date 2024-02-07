import os
from shutil import rmtree
from pathlib import Path
from subprocess import run
from git import Repo
import shutil

def download_directory(github_url=None):
    if github_url is None:
        repo_url = input("Enter the repository url: ")
    else:
        repo_url = github_url
        repoAuthor = repo_url.split('/')[3]
        repoName = repo_url.split('/')[4]
        print(f"Repo Author: {repoAuthor}")
        print(f"Repo Name: {repoName}")
        author_repoName = repoAuthor + "_" + repoName
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
    data_backup_path = "repodata_txt"
    if os.path.exists(data_backup_path):
        rmtree(data_backup_path)

    # for each file in RepoContents, copy it to data_backup if the file is readable as a text file, and convert it to a .txt file in the data_backup folder
    for root, path, files in os.walk(target_path):
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
                    text_file_name = text_file_name.replace('RepoContents/', '')

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

download_directory()

try:
    shutil.rmtree("RepoContents")
    print(f"SUCCESS: Deleted directory RepoContents")
except Exception as e:
    print(f"Error: {e}")
