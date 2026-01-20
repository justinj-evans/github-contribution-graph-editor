import os
from git import Repo
import tempfile
import subprocess
import streamlit as st
import shutil
import time
from tempfile import TemporaryDirectory

def branch_exists(repo_url, branch_name):
    result = subprocess.run(
        ["git", "ls-remote", "--heads", repo_url, branch_name],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def github_upload_commits(REPO_URL, GIT_USERNAME, GIT_EMAIL, GITHUB_TOKEN, commit_date_counts: dict):
    # Configuration variables
    BRANCH = 'Automation'
    COMMIT_MESSAGE = "Automated commit to populate contribution graph"

    # Create temporary directory manually for better control
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning {REPO_URL} (branch: {BRANCH}) into {temp_dir}")

        # Determine if branch exists before cloning
        if branch_exists(REPO_URL, BRANCH):
            repo = Repo.clone_from(REPO_URL, temp_dir, branch=BRANCH)
        else:
            repo = Repo.clone_from(REPO_URL, temp_dir)  # default branch

        # Set authenticated remote URL with token (GitHub uses token@ not username:token@)
        authenticated_url = REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
        repo.git.remote(
            "set-url",
            "origin",
            authenticated_url
        )
        
        # Disable credential helper to force use of embedded token in URL
        with repo.config_writer() as git_config:
            git_config.set_value("credential", "helper", "").release()

        # Define dummy file path
        file_path = os.path.join(temp_dir, "activity.log")

        with open(file_path, "w") as f:
            f.write(f"Starting activity log.\n")

        # Set Git user identity
        repo.config_writer().set_value("user", "name", GIT_USERNAME).release()
        repo.config_writer().set_value("user", "email", GIT_EMAIL).release()

        # Ensure at least one commit exists before pushing
        if not repo.head.is_valid():
            repo.index.add([file_path])
            repo.index.commit("Initial commit to set up repository")

        # Generate commits for past DAYS_TO_BACKFILL days
        # commit_date_counts is a dict of date strings to number of commits
        # date_dict[day.strftime("%Y-%m-%d")] = value
        for date in commit_date_counts:
            commit_date_str = date
            num_commits = commit_date_counts[date]

            # only submit if commit count > 0
            if num_commits > 0:
                print(f"Creating {num_commits} commits on {commit_date_str}")
                for _ in range(num_commits):
                    with open(file_path, "a") as f:
                        f.write(f"Commit on {commit_date_str}\n")

                    repo.index.add([file_path])
                    repo.index.commit(
                        COMMIT_MESSAGE, author_date=commit_date_str, commit_date=commit_date_str
                    )

        # Push changes using direct git command (bypasses credential helpers)
        try:
            repo.git.push("origin", f"HEAD:{BRANCH}", "-f")
            print(f"Pushed changes to {REPO_URL} on branch {BRANCH}")
        except Exception as e:
            print(f"Error pushing to repository: {e}")
            raise
        
    finally:
        # Ensure git releases all locks before cleanup
        time.sleep(0.5)
        # Remove temporary directory
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not fully clean up temp directory {temp_dir}: {e}")
