import os
import requests

import requests
from pathlib import Path
import time

# Global variables
API_BASE_URL = 'https://api.github.com'
ACCESS_TOKEN = 'your_access_token_here'

# Function to handle API requests with rate limiting
def make_api_request(url, headers=None, params=None):
    response = requests.get(url, headers=headers, params=params)
    
    # Check for rate limiting
    remaining_requests = int(response.headers.get('X-RateLimit-Remaining', 0))
    if remaining_requests == 0:
        reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
        sleep_time = reset_time - time.time() + 1  # Add 1 second to be safe
        print(f"Rate limit reached. Waiting for {sleep_time} seconds...")
        time.sleep(sleep_time)
        response = requests.get(url, headers=headers, params=params)
    
    return response

def get_repos(url, access_token):
    headers = {'Authorization': f'token {access_token}'}
    response = make_api_request(
        url='https://api.github.com/user/repos', 
        headers=headers,
        # params={
        #         "visibility":"all",
        #         "type":"all",
        #         "sort":"created",
        #         "direction":"desc"
        #     }
        )
    # response = requests.get('https://api.github.com/user/repos', headers=headers)
    repos = response.json()
    return repos

# Function to fetch and save repository contents with pagination support
def fetch_and_save_repo_contents(repo_owner, repo_name, auth_token):
    headers = {'Authorization': f'token {access_token}'}
    contents_url = f"{API_BASE_URL}/repos/{repo_owner}/{repo_name}/contents"
    
    def fetch_contents(url, path=""):
        response = make_api_request(url, headers=headers)
        response.raise_for_status()
        contents = response.json()
        
        for content in contents:
            if content['type'] == 'dir':
                fetch_contents(content['url'], path + content['name'] + "/")
            elif content['type'] == 'file':
                if not any(content['name'].endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                    file_response = make_api_request(content['download_url'], headers=headers)
                    file_response.raise_for_status()
                    Path(f"repo_contents/{path}").mkdir(parents=True, exist_ok=True)
                    with open(f"repo_contents/{path}{content['name']}", 'w') as file:
                        file.write(file_response.text)
    
    fetch_contents(contents_url)

# def fetch_and_save_repo_contents(repo_full_name, access_token):
#     headers = {'Authorization': f'token {access_token}'}
#     contents_url = f'https://api.github.com/repos/{repo_full_name}/contents'
#     response = requests.get(contents_url, headers=headers)
#     contents = response.json()
    
#     for content in contents:
#         if content['type'] == 'file' and not content['name'].endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
#             file_response = requests.get(content['download_url'])
#             file_path = os.path.join('repo_contents', content['name'])
#             with open(file_path, 'w') as file:
#                 file.write(file_response.text)

# def fetch_and_save_repo_contents(repo_owner, repo_name, auth_token):
#     headers = {'Authorization': f'token {auth_token}'}
#     contents_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    
#     def fetch_contents(url, path=""):
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         contents = response.json()
        
#         for content in contents:
#             if content['type'] == 'dir':
#                 fetch_contents(content['url'], path + content['name'] + "/")
#             elif content['type'] == 'file':
#                 # Skipping image files
#                 if not any(content['name'].endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
#                     file_response = requests.get(content['download_url'], headers=headers)
#                     file_response.raise_for_status()
#                     # Ensure directory exists
#                     Path(f"repo_contents/{path}").mkdir(parents=True, exist_ok=True)
#                     with open(f"repo_contents/{path}{content['name']}", 'w') as file:
#                         file.write(file_response.text)
    
#     fetch_contents(contents_url)

# Function to fetch and save issues with pagination support
def save_issues(repo_owner, repo_name):
    headers = {'Authorization': f'token {access_token}'}
    issues_url = f"{API_BASE_URL}/repos/{repo_owner}/{repo_name}/issues"
    
    def fetch_and_save_issues(url):
        response = make_api_request(url, headers=headers)
        response.raise_for_status()
        issues = response.json()
        
        with Path(f"{repo_name}_issues.txt").open("a") as f_issues:
            for issue in issues:
                if 'pull_request' not in issue:
                    f_issues.write(f"{issue['title']} - {issue['body']}\n")
        
        # Check for pagination
        link_header = response.headers.get('Link')
        if link_header and 'rel="next"' in link_header:
            next_url = link_header.split(';')[0][1:-1]  # Extract URL from Link header
            fetch_and_save_issues(next_url)
    
    fetch_and_save_issues(issues_url)

# def fetch_issues_and_pulls(repo_full_name, access_token):
#     headers = {'Authorization': f'token {access_token}'}
#     issues_url = f'https://api.github.com/repos/{repo_full_name}/issues'
#     pulls_url = f'https://api.github.com/repos/{repo_full_name}/pulls'
    
#     # Fetch issues
#     issues_response = requests.get(issues_url, headers=headers)
#     issues = issues_response.json()
#     with open('issues.txt', 'w') as file:
#         for issue in issues:
#             file.write(f"{issue['title']}\n{issue['body']}\n\n")
    
#     # Fetch pull requests
#     pulls_response = requests.get(pulls_url, headers=headers)
#     pulls = pulls_response.json()
#     with open('pulls.txt', 'w') as file:
#         for pull in pulls:
#             file.write(f"{pull['title']}\n{pull['body']}\n\n")

# Step 5: Collect Issues and Pull Requests
# def save_issues_and_prs(repo_owner, repo_name, auth_token):
#     headers = {'Authorization': f'token {auth_token}'}
    
#     # Issues (excluding pull requests)
#     issues_response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues", headers=headers)
#     issues_response.raise_for_status()

#     # When saving issues, filter out pull requests by checking if 'pull_request' key is absent
#     with Path(f"{repo_name}_issues.txt").open("w") as f_issues:
#         for issue in issues_response.json():
#             if 'pull_request' not in issue:  # This line filters out pull requests
#                 f_issues.write(f"{issue['title']} - {issue['body']}\n")

#     # Pull Requests
#     prs_response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls", headers=headers)
#     prs_response.raise_for_status()

#     with Path(f"{repo_name}_pulls.txt").open("w") as f_pulls:
#         for pr in prs_response.json():
#             f_pulls.write(f"{pr['title']} - {pr['body']}\n")

# # Main execution
# repo_owner = 'owner_username'
# repo_name = 'repository_name'

# fetch_and_save_repo_contents(repo_owner, repo_name, ACCESS_TOKEN)
# save_issues(repo_owner, repo_name)

def select_repo(repos):
    for i, repo in enumerate(repos):
        print(f"{i+1}: {repo['full_name']}")
    choice = input("Select a repo by number or enter a repo URL: ")
    if choice.isdigit():
        selected_repo = repos[int(choice) - 1]
        return selected_repo['full_name']
    else:
        return choice  # Assuming the user entered a valid GitHub repo URL

