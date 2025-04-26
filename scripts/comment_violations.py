#!/usr/bin/env python3
"""---
title: "Comment License Violations"
name: "comment_violations.py"
description: "Reads disallowed licenses and comments violations on a PR via GitHub API."
category: script
usage: "python scripts/comment_violations.py"
behavior: "Fetches GitHub event data, reads violation report, and posts comments."
inputs: "GITHUB_EVENT_PATH, GITHUB_REPOSITORY, GITHUB_TOKEN"
outputs: "Console logs and GitHub PR comments"
dependencies: "PyGithub"
author: "Byron Williams"
last_modified: "2025-04-26"
changelog: "Add metadata, refactor to Path API, add docstrings, fix lint errors"
tags: [docs, tools]
---

Module: comment_violations

This script reads a list of disallowed licenses from a report file and
posts a comment on the associated GitHub pull request using the GitHub API.

Functions:
    main(): Entry point to process the GitHub event, read violations,
            and post comments on the PR.
"""

import json
import os
from pathlib import Path

from github import Github


def main() -> None:
    """Load the GitHub event payload, read license violations from the report,
    and post a formatted comment to the pull request.

    Raises:
        RuntimeError: If GITHUB_TOKEN is unset for authentication.
        FileNotFoundError: If event payload or report file is missing.

    """
    # Get GitHub event data
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        print(
            "GITHUB_EVENT_PATH is not set or file does not exist; "
            "skipping comments.",
        )
        return

    with Path(event_path).open() as f:
        event = json.load(f)

    pr = event.get("pull_request")
    if not pr:
        print("Not a pull_request event; no comment will be posted.")
        return

    pr_number = pr.get("number")
    repo_full = os.getenv("GITHUB_REPOSITORY")

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        message = (
            "GITHUB_TOKEN is not set; cannot authenticate to GitHub."
        )
        raise RuntimeError(message)

    # Read violations
    report_path = Path("docs/reports/json/disallowed.txt")
    if not report_path.exists():
        print(
            f"Violation report {report_path} not found; nothing to comment.",
        )
        return

    with report_path.open() as f:
        violations = f.read().strip()
    count = len(violations.splitlines()) if violations else 0

    # Construct comment body
    comment = (
        f"### License Scan Results\n\n"
        f"⚠️ **{count} license violations found:**\n\n"
        f"```\n{violations}\n```"
    )

    # Post comment
    gh = Github(token)
    repo = gh.get_repo(repo_full)
    issue = repo.get_issue(number=pr_number)
    issue.create_comment(body=comment)
    print(f"Posted comment on PR #{pr_number} with {count} violations.")


if __name__ == "__main__":
    main()
