import sys
from pathlib import Path

def load_issue(issue_number):
    path = Path(f"./docs/phases/issues/issue_{issue_number}_expanded.md")
    if not path.exists():
        raise FileNotFoundError(f"Issue #{issue_number} not found in expected location: {path}")
    return path.read_text()

def generate_review(issue_number, issue_title):
    base_template_path = Path("./docs/reviews/review_request_template.md")
    if not base_template_path.exists():
        raise FileNotFoundError("Base review request template not found.")
    template = base_template_path.read_text()

    issue_block = load_issue(issue_number).strip()
    result = template.replace("[INSERT_ISSUE_NUMBER]", str(issue_number))
    result = result.replace("[INSERT_ISSUE_TITLE]", issue_title)
    result = result.replace("[Paste full issue markdown here]", issue_block)

    output_path = Path(f"./docs/reviews/review_issue_{issue_number}.md")
    output_path.write_text(result)
    print(f"Review request generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_review_request.py <issue_number> \"<issue_title>\"")
        sys.exit(1)

    issue_num = int(sys.argv[1])
    issue_title = sys.argv[2]
    generate_review(issue_num, issue_title)
