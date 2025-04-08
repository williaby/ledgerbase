import sys
from pathlib import Path

# No additional imports needed for these type hints


# Add type hints for the parameter (int) and return value (str)
def load_issue(issue_number: int) -> str:
    """Loads the expanded issue markdown text from the expected file path."""
    # Path objects handle path logic cleanly
    path = Path(f"./docs/phases/issues/issue_{issue_number}_expanded.md")
    if not path.exists():
        # Use f-string for cleaner error message formatting
        raise FileNotFoundError(
            f"Issue #{issue_number} not found in expected location: {path}"
        )
    return path.read_text()


# Add type hints for parameters (int, str) and specify no return value (None)
def generate_review(issue_number: int, issue_title: str) -> None:
    """Generates a review request markdown file from a template and issue details."""
    base_template_path = Path("./docs/reviews/review_request_template.md")
    if not base_template_path.exists():
        raise FileNotFoundError(
            f"Base review request template not found at {base_template_path}"
        )
    template: str = base_template_path.read_text()  # Hint template variable type

    # Hint intermediate variable types
    issue_block: str = load_issue(issue_number).strip()
    result: str = template.replace("[INSERT_ISSUE_NUMBER]", str(issue_number))
    result = result.replace("[INSERT_ISSUE_TITLE]", issue_title)
    result = result.replace("[Paste full issue markdown here]", issue_block)

    output_path = Path(f"./docs/reviews/review_issue_{issue_number}.md")
    # Ensure parent directory exists if needed
    # output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        result, encoding="utf-8"
    )  # Specify encoding often good practice
    print(f"Review request generated: {output_path}")


if __name__ == "__main__":
    # Check number of arguments before trying to access them
    if len(sys.argv) != 3:
        # Use a more informative error message
        print("Error: Incorrect number of arguments provided.", file=sys.stderr)
        print(
            'Usage: python generate_review_request.py <issue_number> "<issue_title>"',
            file=sys.stderr,
        )
        sys.exit(1)  # Exit with non-zero status to indicate error

    try:
        # Add type hints for clarity in this scope
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
    except FileNotFoundError as e:
        print(f"Error generating review: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # Catch other potential errors during generation
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
