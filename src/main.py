import argparse

from writer import convert_grid_to_dates, generate_commit_data, apply_letter_overlay
from github_interaction import github_upload_commits


def parse_args():
    parser = argparse.ArgumentParser(description="action.yml arguments")
    parser.add_argument("--message", type=str, help="Commit message (case-insensitive)")


class github_contribution_graph:
    def __init__(self, args):
        self.message = args.message

    def message(self):
        # user supplied message generates dates
        commit_data = generate_commit_data()
        commit_data = apply_letter_overlay(commit_data, "    HI")

        # Export expected commit_graph for debugging
        # plot_commit_graph(commit_data)

        # reverse engineer commit dates from commit graph
        self.commit_date_counts = convert_grid_to_dates(commit_data)

    def push_github_commits(self):
        github_upload_commits(self.commit_date_counts, repo_url=None, branch=None)


if __name__ == "__main__":
    args = parse_args()
    graph = github_contribution_graph(args)
    graph.message()
    graph.push_github_commits()
