import sys
from pathlib import Path

# Define a constant for the expected number of arguments
EXPECTED_ARG_COUNT = 3


def load_issue(issue_number: int) -> str:
    """Load the expanded issue markdown text from the expected file path."""
    path = Path(f"./docs/phases/issues/issue_{issue_number}_expanded.md")
    if not path.exists():
        msg = f"Issue #{issue_number} not found in expected location: {path}"
        raise FileNotFoundError(msg)
    return path.read_text()


def generate_review(issue_number: int, issue_title: str) -> None:
    """Generate a review request markdown file from a template and issue details."""
    base_template_path = Path("./docs/reviews/review_request_template.md")
    if not base_template_path.exists():
        msg = f"Base review request template not found at {base_template_path}"
        raise FileNotFoundError(msg)
    template: str = base_template_path.read_text()

    issue_block: str = load_issue(issue_number).strip()
    result: str = template.replace("[INSERT_ISSUE_NUMBER]", str(issue_number))
    result = result.replace("[INSERT_ISSUE_TITLE]", issue_title)
    result = result.replace("[Paste full issue markdown here]", issue_block)

    output_path = Path(f"./docs/reviews/review_issue_{issue_number}.md")
    output_path.write_text(result, encoding="utf-8")
    print(f"Review request generated: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != EXPECTED_ARG_COUNT:
        print("Error: Incorrect number of arguments provided.", file=sys.stderr)
        print(
            'Usage: python generate_review_request.py <issue_number> "<issue_title>"',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        issue_num: int = int(sys.argv[1])
        issue_title: str = sys.argv[2]
    except ValueError:
        print(
            f"Error: <issue_number> must be an integer. Received: '{sys.argv[1]}'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        generate_review(issue_num, issue_title)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error generating review: {e}", file=sys.stderr)
        sys.exit(1)
