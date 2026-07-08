import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NEGATIVE_GUARDRAIL_MARKERS = (
    "不得",
    "不要",
    "禁止",
    "不应",
    "must not",
    "do not",
    "should not",
    "not ",
)


def runtime_markdown_files():
    for base in [ROOT / "commands", ROOT / "skills"]:
        yield from sorted(base.rglob("*.md"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def executable_instruction_lines(text: str):
    for line in text.splitlines():
        normalized = line.lower()
        if any(marker in normalized for marker in NEGATIVE_GUARDRAIL_MARKERS):
            continue
        yield line


def assert_no_runtime_matches(pattern: str, *, message: str) -> None:
    regex = re.compile(pattern)
    matches = []
    for path in runtime_markdown_files():
        candidate_text = "\n".join(executable_instruction_lines(read(path)))
        if regex.search(candidate_text):
            matches.append(path.relative_to(ROOT).as_posix())
    assert not matches, f"{message}: {matches}"


def test_runtime_prompts_do_not_reference_maintainer_docs_or_old_contracts():
    assert_no_runtime_matches(
        r"docs/maintainers",
        message="runtime prompts must not use maintainer docs as execution context",
    )
    assert_no_runtime_matches(
        r"docs/CURRENT_ARTIFACT_CONTRACTS\.md",
        message="runtime prompts must not reference the old artifact contract path",
    )
    assert_no_runtime_matches(
        r"Core artifacts include",
        message="runtime prompts must not embed the full artifact tree heading",
    )


def test_runtime_prompts_do_not_bulk_read_examples():
    assert_no_runtime_matches(
        r"examples/\*\*",
        message="runtime prompts must not bulk-read examples as default context",
    )
    assert_no_runtime_matches(
        r"Demo task files",
        message="runtime prompts must not maintain a demo task catalog",
    )


def test_command_and_core_are_not_demo_task_catalogs():
    for path in [
        ROOT / "commands/write.md",
        ROOT / "skills/writing-core/SKILL.md",
    ]:
        text = read(path)
        demo_task_paths = re.findall(r"examples/[^\s`\"']+task\.yaml", text)
        assert len(demo_task_paths) <= 1, (
            f"{path.relative_to(ROOT)} looks like an examples task catalog: "
            f"{demo_task_paths}"
        )


def test_document_type_input_steps_do_not_own_shared_run_start():
    patterns = [
        r"创建\s+`?runs/<run_id>`?",
        r"创建\s+run\s*目录",
        r"写入\s+manifest",
        r"写\s+manifest",
        r"写入\s+.*task_brief",
        r"写\s+.*task_brief",
    ]
    regexes = [re.compile(pattern) for pattern in patterns]
    matches = []
    for path in sorted((ROOT / "skills/document-types").glob("*/steps/step-input-materials.md")):
        text = "\n".join(executable_instruction_lines(read(path)))
        for regex in regexes:
            if regex.search(text):
                matches.append((path.relative_to(ROOT).as_posix(), regex.pattern))
    assert not matches, f"document-type overlays must not own run start artifacts: {matches}"


def test_runtime_prompts_delegate_run_start_to_engine():
    required = "python -m ai_writing_plugin init-run --task <task.yaml>"
    for path in [
        ROOT / "commands/write.md",
        ROOT / "skills/workflow-steps/step-input-materials/SKILL.md",
    ]:
        assert required in read(path)
