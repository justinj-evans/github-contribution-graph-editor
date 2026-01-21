# Development
This document explains how to set up a development environment to contribute to *github-contribution-graph-editor*.

## Project Structure

```
src/
├── app.py              # Streamlit web application
├── writer.py           # Core logic for generating commit patterns
├── github_interaction.py  # GitHub API interactions
├── grid.py             # Grid manipulation utilities
├── dates.py            # Date handling utilities
├── map.py              # Mapping functions
```

## Setting up a virtual environment
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/github-contribution-graph-editor.git
   cd github-contribution-graph-editor
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

   Or using uv (recommended):
   ```bash
   uv sync
   ```

## Branch Naming
Branches follow the scheme: `type-number-summary`

Examples:
- `feature-1-add-random-fill`
- `bugfix-2-fix-date-conversion`
- `doc-3-update-readme`

Accepted types:
- `feature`: New functionality
- `bugfix`: Bug fixes
- `doc`: Documentation updates