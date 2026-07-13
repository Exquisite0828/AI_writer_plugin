import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_FIXTURE_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yaml", ".yml"}
REMOVED_CLI_COMMANDS = (
    "write-run",
    "resume-run",
    "ingest-run",
    "outline-run",
    "evidence-run",
    "plan-run",
    "draft-run",
    "review-run",
    "finalize-run",
    "learning-run",
    "profile-from-spec",
    "profile-promote",
    "correction-harvest",
    "prepare-stage-review",
    "validate-stage-review",
    "record-stage-review-decision",
    "check-stage-review-gate",
)


def text_fixture_files():
    for path in sorted((ROOT / "examples").rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_FIXTURE_SUFFIXES:
            yield path


def test_current_example_fixtures_do_not_reference_removed_cli_commands():
    command_pattern = re.compile(
        rf"(?<![a-z0-9-])(?:{'|'.join(map(re.escape, REMOVED_CLI_COMMANDS))})(?![a-z0-9-])",
        re.IGNORECASE,
    )
    matches = []

    for path in text_fixture_files():
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for match in command_pattern.finditer(line):
                matches.append(
                    (
                        path.relative_to(ROOT).as_posix(),
                        line_number,
                        match.group(0),
                    )
                )

    assert not matches, f"current example fixtures reference removed CLI commands: {matches}"
