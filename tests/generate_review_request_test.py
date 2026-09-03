"""Unit tests for the review-request generator script."""

import importlib.util
import sys
from pathlib import Path

import pytest

# The repository root also ships a `scripts` package, so `src/scripts` cannot be
# imported by name without ambiguity. Load the module under test by path.
_MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "scripts"
    / "generate_review_request.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "ledgerbase_generate_review_request",
    _MODULE_PATH,
)
assert _SPEC is not None
assert _SPEC.loader is not None
grr = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = grr
_SPEC.loader.exec_module(grr)

EXPECTED_ARG_COUNT = 3


def _seed_issue(root: Path, number: int, body: str) -> Path:
    issue_dir = root / "docs" / "phases" / "issues"
    issue_dir.mkdir(parents=True, exist_ok=True)
    path = issue_dir / f"issue_{number}_expanded.md"
    path.write_text(body, encoding="utf-8")
    return path


def _seed_template(root: Path, body: str) -> Path:
    review_dir = root / "docs" / "reviews"
    review_dir.mkdir(parents=True, exist_ok=True)
    path = review_dir / "review_request_template.md"
    path.write_text(body, encoding="utf-8")
    return path


def test_expected_arg_count() -> None:
    """The script expects the program name plus two arguments."""
    assert grr.EXPECTED_ARG_COUNT == EXPECTED_ARG_COUNT


def test_load_issue_returns_file_contents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """load_issue reads the expanded issue markdown from the expected path."""
    monkeypatch.chdir(tmp_path)
    _seed_issue(tmp_path, 7, "issue body")
    assert grr.load_issue(7) == "issue body"


def test_load_issue_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """load_issue raises when the issue file is absent."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="Issue #7"):
        grr.load_issue(7)


def test_generate_review_missing_template(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """generate_review raises when the base template is absent."""
    monkeypatch.chdir(tmp_path)
    _seed_issue(tmp_path, 7, "issue body")
    with pytest.raises(FileNotFoundError, match="Base review request template"):
        grr.generate_review(7, "Some title")


def test_generate_review_writes_substituted_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """generate_review substitutes every placeholder and writes the result."""
    monkeypatch.chdir(tmp_path)
    _seed_issue(tmp_path, 7, "  issue body  ")
    _seed_template(
        tmp_path,
        "# Review [INSERT_ISSUE_NUMBER]: [INSERT_ISSUE_TITLE]\n"
        "[Paste full issue markdown here]\n",
    )

    grr.generate_review(7, "Some title")

    output = (tmp_path / "docs" / "reviews" / "review_issue_7.md").read_text(
        encoding="utf-8",
    )
    assert "# Review 7: Some title" in output
    assert "issue body" in output
    assert "[INSERT_ISSUE_NUMBER]" not in output
    assert "[INSERT_ISSUE_TITLE]" not in output
    assert "[Paste full issue markdown here]" not in output
