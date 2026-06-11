import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_ROOT_ENTRIES = [
    "plugin.json",
    "agents",
    "scripts",
    "hooks",
    "monitors",
    ".mcp.json",
    ".lsp.json",
    "settings.json",
]

FORBIDDEN_DEPENDENCIES = [
    "langchain",
    "llama-index",
    "chromadb",
    "faiss",
    "pinecone",
    "weaviate",
    "openai",
    "anthropic",
]


def test_plugin_manifest_exists_and_points_to_write_command() -> None:
    manifest_path = REPO_ROOT / ".claude-plugin" / "plugin.json"

    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["name"] == "ai-writing-plugin"
    assert manifest["description"]
    assert manifest["version"]
    assert "./commands/write.md" in manifest["commands"]
    assert not (REPO_ROOT / "plugin.json").exists()


def test_write_command_exists_and_is_actionable() -> None:
    command_path = REPO_ROOT / "commands" / "write.md"

    assert command_path.exists()
    command = command_path.read_text(encoding="utf-8")
    for required in [
        "$ARGUMENTS",
        "/ai-writing-plugin:write",
        "/write",
        "ingest-run",
        "outline-run",
        "evidence-run",
        "plan-run",
        "draft-run",
        "review-run",
        "finalize-run",
        "learning-run",
        "record-hitl",
        "NEEDS_USER_CONFIRMATION",
        "sample documents",
        "expected_output_shape",
        "candidate",
        "proposed",
    ]:
        assert required in command


def test_no_forbidden_phase_8_systems_or_root_plugin_created() -> None:
    for entry in FORBIDDEN_ROOT_ENTRIES:
        assert not (REPO_ROOT / entry).exists(), entry


def test_no_external_framework_dependencies_added() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    package_sources = "\n".join(path.read_text(encoding="utf-8").lower() for path in (REPO_ROOT / "ai_writing_plugin").glob("*.py"))
    combined = f"{pyproject}\n{package_sources}"

    for dependency in FORBIDDEN_DEPENDENCIES:
        assert dependency not in combined


def test_phase_8_current_docs_are_present_and_synced() -> None:
    expected_docs = [
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "CURRENT_ARTIFACT_CONTRACTS.md",
        REPO_ROOT / "docs" / "RUNBOOK.md",
        REPO_ROOT / "docs" / "maintainers" / "ARCHITECTURE.md",
    ]

    for doc_path in expected_docs:
        assert doc_path.exists(), doc_path

    contracts = (REPO_ROOT / "docs" / "CURRENT_ARTIFACT_CONTRACTS.md").read_text(encoding="utf-8")
    runbook = (REPO_ROOT / "docs" / "RUNBOOK.md").read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    for artifact_path in [
        "trace/session_trace.jsonl",
        "trace/hitl_decisions.jsonl",
        "learning/run_summary.md",
        "learning/reusable_patterns.md",
        "learning/candidate_profile_update.yaml",
        "learning/candidate_skill_patch.md",
        "learning/promotion_report.md",
    ]:
        assert artifact_path in contracts
    for required in ["write-run", "learning-run", "record-hitl", "/ai-writing-plugin:write"]:
        assert required in runbook
    assert "历史 phase docs" in docs_index
    assert "不是当前执行指令" in docs_index
