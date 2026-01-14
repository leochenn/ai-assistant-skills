---
name: github-star-exporter
description: Fetches all GitHub repositories starred by the user and exports them to a formatted Markdown file. Supports sorting by star date or star count, and includes metadata like language, star count, and update dates. Use this skill when the user wants to backup, list, or organize their GitHub stars.
---

# GitHub Star Exporter

This skill allows you to export your GitHub starred repositories to a Markdown file.

## Prerequisites

- **GitHub Token**: A valid GitHub Personal Access Token (PAT).
- **Python**: Python environment with `requests` library installed.

## Usage

Use `run_shell_command` to execute the bundled Python script.

### Command Syntax

```powershell
python ".gemini/skills/github-star-exporter/scripts/export_stars.py" --token "<YOUR_GITHUB_TOKEN>" [--output "<OUTPUT_FILENAME>"] [--sort <star_date|stars>]
```

### Parameters

- `--token`: (Required) Your GitHub Personal Access Token.
- `--output`: (Optional) The output filename (e.g., `stars.md`). If omitted, a timestamped filename is generated.
- `--sort`: (Optional) Sorting method.
    - `star_date` (Default): Sort by the date you starred the repo (Newest first).
    - `stars`: Sort by the number of stars the repo has (Highest first).

### Examples

**1. Default Export (Sorted by Star Date)**

```powershell
python ".gemini/skills/github-star-exporter/scripts/export_stars.py" --token "ghp_xxxxxxxxxxxx"
```

**2. Specify Output File**

```powershell
python ".gemini/skills/github-star-exporter/scripts/export_stars.py" --token "ghp_xxxxxxxxxxxx" --output "my_stars.md"
```

**3. Sort by Star Count**

```powershell
python ".gemini/skills/github-star-exporter/scripts/export_stars.py" --token "ghp_xxxxxxxxxxxx" --sort stars --output "popular_stars.md"
```
