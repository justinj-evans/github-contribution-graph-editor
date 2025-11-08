import os
from git import Repo
import tempfile
import subprocess

from dotenv import load_dotenv


def branch_exists(repo_url, branch_name):
    result = subprocess.run(
        ["git", "ls-remote", "--heads", repo_url, branch_name],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def github_upload_commits(commit_date_counts, repo_url, branch):
    # TODO: convert .env to args method
    # Load environment variables from .env file
    load_dotenv()

    # Configuration variables
    REPO_URL = os.getenv("REPO_URL", "https://github.com/your-username/your-repo.git")
    BRANCH = os.getenv("GIT_BRANCH", "main")
    COMMIT_MESSAGE = os.getenv(
        "GIT_COMMIT_MESSAGE", "Automated commit to populate contribution graph"
    )
    GIT_USERNAME = os.getenv("GIT_USERNAME", "your-username")
    GIT_EMAIL = os.getenv("GIT_EMAIL", "your-email@example.com")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # Clone the repo to a temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Cloning {REPO_URL} (branch: {BRANCH}) into {temp_dir}")

    # Determine if branch exists before cloning
    if branch_exists(REPO_URL, BRANCH):
        repo = Repo.clone_from(REPO_URL, temp_dir, branch=BRANCH)
    else:
        repo = Repo.clone_from(REPO_URL, temp_dir)  # default branch

    # Define dummy file path
    file_path = os.path.join(temp_dir, "dummy.txt")

    # Set Git user identity
    repo.config_writer().set_value("user", "name", GIT_USERNAME).release()
    repo.config_writer().set_value("user", "email", GIT_EMAIL).release()

    # Wipe commit history
    repo.git.checkout("--orphan", "temp_branch")
    repo.git.commit("--allow-empty", "-m", "Initial empty commit")
    if branch_exists(REPO_URL, BRANCH):
        repo.git.branch("-D", BRANCH)
    repo.git.branch("-m", BRANCH)
    repo.git.push("--force", "origin", BRANCH)

    # Ensure at least one commit exists before pushing
    if not repo.head.is_valid():
        repo.index.add([file_path])
        repo.index.commit("Initial commit to set up repository")

    # Generate commits for past DAYS_TO_BACKFILL days
    for i in commit_date_counts:
        commit_date_str, num_commits = i

        for _ in range(num_commits):
            with open(file_path, "a") as f:
                f.write(f"Commit on {commit_date_str}\n")

            repo.index.add([file_path])
            repo.index.commit(
                COMMIT_MESSAGE, author_date=commit_date_str, commit_date=commit_date_str
            )  # FIXED

    # Push changes
    origin = repo.remote()  # name="origin"
    origin.push(refspec=f"{BRANCH}:{BRANCH}", force=True)
