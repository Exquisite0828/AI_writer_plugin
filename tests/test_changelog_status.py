from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
STALE_TSC_NOTE = (
    "- TSC / Technical Safety Concept is deferred and not implemented as an "
    "official type, profile, Skill, fixture, or test target."
)


def changelog_sections():
    text = CHANGELOG.read_text(encoding="utf-8")
    unreleased, release_0_1_0 = text.split("## [0.1.0] - 2026-06-08", 1)
    return text, unreleased, release_0_1_0


def test_unreleased_changelog_records_current_nonofficial_tsc_status():
    _, unreleased, _ = changelog_sections()

    assert "`TechnicalSafetyConcept` (TSC) Skill-layer prototype" in unreleased
    assert "document-type Skill, step overlays, and an opt-in demo fixture" in unreleased
    assert "TSC is not an official L3 built-in" in unreleased
    assert "no Python rules/registry, end-to-end content CLI, or dedicated engine test" in unreleased
    assert "Official L3 TSC and HSC/SSC remain deferred" in unreleased


def test_0_1_0_tsc_note_is_explicitly_historical():
    text, _, release_0_1_0 = changelog_sections()

    assert STALE_TSC_NOTE not in text
    assert "At the 0.1.0 release" in release_0_1_0
    assert "Nonofficial prototype assets were added after this release" in release_0_1_0


def test_documented_tsc_prototype_assets_exist():
    skill_root = ROOT / "skills" / "document-types" / "TechnicalSafetyConcept"
    fixture_root = ROOT / "examples" / "technical_safety_concept_demo_fixture"

    assert (skill_root / "SKILL.md").is_file()
    assert list((skill_root / "steps").glob("step-*.md"))
    assert (fixture_root / "task.yaml").is_file()


def test_unreleased_changelog_records_current_runtime_closure_changes():
    _, unreleased, _ = changelog_sections()

    assert "`build-stage-review-issues` and `validate-stage-review-issues`" in unreleased
    assert "current CLI now exposes 19 commands" in unreleased
    assert "propagates real upstream StepResult artifacts" in unreleased
    assert "independently optional and lazily loaded" in unreleased
    assert "transactional review-cycle boundary" in unreleased
    assert "`complete-step-worker-dispatch --status` is now an assertion" in unreleased
