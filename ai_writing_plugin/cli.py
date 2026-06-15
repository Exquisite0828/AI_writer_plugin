from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .draft import DraftRunError
from .evidence import EvidenceRunError
from .finalize import FinalizeRunError
from .learning import LearningRunError
from .outline import OutlineRunError
from .planning import PlanRunError
from .review import ReviewRunError
from .run_manager import (
    InitRunError,
    ResumeRunError,
    WriteRunError,
    draft_run,
    evidence_run,
    finalize_run,
    ingest_run,
    init_run,
    learning_run,
    outline_run,
    plan_run,
    record_hitl,
    resume_run,
    review_run,
    write_run,
)
from .stage_review import (
    STAGE_REVIEW_DECISIONS,
    StageReviewError,
    check_stage_review_gate,
    prepare_stage_review,
    record_stage_review_decision,
    validate_stage_review,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai_writing_plugin")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_run_parser = subparsers.add_parser("init-run", help="Create a Phase 0 run.")
    init_run_parser.add_argument("--task", required=True, help="Path to task.yaml.")
    init_run_parser.add_argument(
        "--runs-dir",
        default="runs",
        help="Directory where run outputs are created. Defaults to runs.",
    )

    ingest_run_parser = subparsers.add_parser("ingest-run", help="Create a Phase 1 run with input ingestion.")
    ingest_run_parser.add_argument("--task", required=True, help="Path to task.yaml.")
    ingest_run_parser.add_argument(
        "--runs-dir",
        default="runs",
        help="Directory where run outputs are created. Defaults to runs.",
    )

    outline_run_parser = subparsers.add_parser("outline-run", help="Create Phase 2 template structure and L1 outline.")
    outline_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing Phase 1 run directory.",
    )

    evidence_run_parser = subparsers.add_parser("evidence-run", help="Create Phase 3 research questions and evidence map.")
    evidence_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing Phase 2 run directory.",
    )

    plan_run_parser = subparsers.add_parser("plan-run", help="Create Phase 4 citation and writing plan artifacts.")
    plan_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing Phase 3 run directory.",
    )

    draft_run_parser = subparsers.add_parser("draft-run", help="Create Phase 5 conservative draft artifacts.")
    draft_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing Phase 4 run directory.",
    )

    review_run_parser = subparsers.add_parser("review-run", help="Create Phase 6 review and verification artifacts.")
    review_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing Phase 5 run directory.",
    )

    finalize_run_parser = subparsers.add_parser("finalize-run", help="Create Phase 7 revision and final delivery artifacts.")
    finalize_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing Phase 6 run directory.",
    )

    learning_run_parser = subparsers.add_parser("learning-run", help="Create Phase 8 trace and learning artifacts.")
    learning_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing Phase 7 run directory.",
    )

    resume_run_parser = subparsers.add_parser("resume-run", help="Resume an interrupted resumable write run.")
    resume_run_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing run directory containing run_state.json.",
    )

    record_hitl_parser = subparsers.add_parser("record-hitl", help="Append a HITL decision to a run trace.")
    record_hitl_parser.add_argument("--run", "--run-dir", dest="run", required=True, help="Existing run directory.")
    record_hitl_parser.add_argument("--stage", required=True, help="HITL stage or gate name.")
    record_hitl_parser.add_argument("--decision", required=True, help="Recorded user decision.")
    record_hitl_parser.add_argument("--comment", default="", help="User comment for the decision.")
    record_hitl_parser.add_argument(
        "--affected-sections",
        default="",
        help="Comma-separated affected section ids.",
    )
    record_hitl_parser.add_argument("--next-action", required=True, help="Next deterministic action.")

    prepare_stage_review_parser = subparsers.add_parser(
        "prepare-stage-review",
        help="Prepare an advisory Claude Code stage review package.",
    )
    prepare_stage_review_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing run directory.",
    )
    prepare_stage_review_parser.add_argument("--stage", required=True, help="Completed stage to prepare for review.")

    validate_stage_review_parser = subparsers.add_parser(
        "validate-stage-review",
        help="Validate advisory Claude Code stage review issues.",
    )
    validate_stage_review_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing run directory.",
    )
    validate_stage_review_parser.add_argument("--stage", required=True, help="Stage whose issues.json should validate.")
    validate_stage_review_parser.add_argument(
        "--issues-file",
        default=None,
        help="Optional issues.json path. Defaults to stage_reviews/<stage>/issues.json under the run.",
    )

    record_stage_review_decision_parser = subparsers.add_parser(
        "record-stage-review-decision",
        help="Record a user stage review gate decision.",
    )
    record_stage_review_decision_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing run directory.",
    )
    record_stage_review_decision_parser.add_argument("--stage", required=True, help="Stage whose review gate is decided.")
    record_stage_review_decision_parser.add_argument(
        "--decision",
        required=True,
        choices=sorted(STAGE_REVIEW_DECISIONS),
        help="Stage review gate decision.",
    )
    record_stage_review_decision_parser.add_argument("--notes", default="", help="Decision notes; required for skipped.")
    record_stage_review_decision_parser.add_argument(
        "--decided-by",
        default="user",
        help="Short identifier for the user/operator recording the decision.",
    )

    check_stage_review_gate_parser = subparsers.add_parser(
        "check-stage-review-gate",
        help="Check whether a validated stage review has a passing user gate decision.",
    )
    check_stage_review_gate_parser.add_argument(
        "--run",
        "--run-dir",
        dest="run",
        required=True,
        help="Existing run directory.",
    )
    check_stage_review_gate_parser.add_argument("--stage", required=True, help="Stage whose review gate should be checked.")

    write_run_parser = subparsers.add_parser("write-run", help="Run the full noninteractive Phase 0-8 writing helper.")
    write_run_parser.add_argument("--task", required=True, help="Path to task.yaml.")
    write_run_parser.add_argument(
        "--runs-dir",
        default="runs",
        help="Directory where run outputs are created. Defaults to runs.",
    )

    profile_from_spec_parser = subparsers.add_parser(
        "profile-from-spec",
        help="Generate an inactive candidate document_profile.yaml package from a Markdown Spec.",
    )
    profile_from_spec_parser.add_argument("--spec", required=True, help="Path to Markdown Spec.")
    profile_from_spec_parser.add_argument("--output-dir", required=True, help="Candidate output directory.")
    profile_from_spec_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite files in the same candidate output directory. Protected paths remain blocked.",
    )
    profile_from_spec_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing candidate files.",
    )
    profile_from_spec_parser.add_argument(
        "--no-skeletons",
        action="store_true",
        help="Only generate document_profile.yaml and candidate_manifest.json.",
    )

    correction_harvest_parser = subparsers.add_parser(
        "correction-harvest",
        help="Harvest human corrections into inactive N7 candidate profile patch artifacts.",
    )
    correction_harvest_parser.add_argument("--run-dir", required=True, help="Run directory for N7 correction artifacts.")
    correction_harvest_parser.add_argument("--corrections", required=True, help="Correction YAML/JSON/JSONL input file.")
    correction_harvest_parser.add_argument("--profile", required=True, help="External document_profile.yaml target baseline.")

    profile_promote_parser = subparsers.add_parser(
        "profile-promote",
        help="Gate and optionally apply an N7 candidate profile patch to an explicit external profile.",
    )
    profile_promote_parser.add_argument("--run-dir", required=True, help="Run directory for promotion context.")
    profile_promote_parser.add_argument("--candidate-patch", required=True, help="candidate_profile_patch.yaml path.")
    profile_promote_parser.add_argument("--eval-report", required=True, help="N6 eval_report.json path.")
    profile_promote_parser.add_argument("--approval", default=None, help="Explicit human approval YAML/JSON file.")
    profile_promote_parser.add_argument("--target-profile", required=True, help="Explicit external document_profile.yaml path.")
    profile_promote_parser.add_argument("--output-dir", required=True, help="Directory for promotion report and rollback artifacts.")
    profile_promote_parser.add_argument("--apply", action="store_true", help="Apply the patch after all gates pass.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-run":
        try:
            run_dir = init_run(task_file=Path(args.task), runs_dir=Path(args.runs_dir))
        except InitRunError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Created run: {run_dir}")
        return 0

    if args.command == "ingest-run":
        try:
            run_dir = ingest_run(task_file=Path(args.task), runs_dir=Path(args.runs_dir))
        except InitRunError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        input_inventory = json.loads((run_dir / "inputs" / "input_inventory.json").read_text(encoding="utf-8"))
        print(f"Created run: {run_dir}")
        print(f"已读取输入材料：{input_inventory['summary']['total_files']} 个文件")
        print("生成的 artifacts:")
        print("- manifest.json")
        print("- task_brief.json")
        print("- inputs/input_inventory.json")
        print("- knowledge/source_index.json")
        print("- knowledge/knowledge_gaps.md")
        return 0

    if args.command == "outline-run":
        try:
            run_dir = outline_run(run_dir=Path(args.run))
        except (OutlineRunError, ResumeRunError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Outlined run: {run_dir}")
        print("大纲生成已完成。")
        print("生成的 artifacts:")
        print("- plans/template_structure.json")
        print("- plans/outline_l1.md")
        return 0

    if args.command == "evidence-run":
        try:
            run_dir = evidence_run(run_dir=Path(args.run))
        except (EvidenceRunError, ResumeRunError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        print("证据映射已完成")
        print(f"Run: {manifest['run_id']}")
        print("生成的 artifacts:")
        print("- plans/research_questions.json")
        print("- plans/evidence_map.json")
        print("- plans/unresolved_questions.md")
        return 0

    if args.command == "plan-run":
        try:
            run_dir = plan_run(run_dir=Path(args.run))
        except (PlanRunError, ResumeRunError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        print("写作计划已完成")
        print(f"Run: {manifest['run_id']}")
        print("生成的 artifacts:")
        print("- plans/citation_plan.json")
        print("- plans/outline_final.md")
        print("- plans/section_tasks.json")
        print("- plans/writing_plan.md")
        return 0

    if args.command == "draft-run":
        try:
            run_dir = draft_run(run_dir=Path(args.run))
        except (DraftRunError, ResumeRunError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        artifact_paths = [
            artifact["path"]
            for artifact in manifest["artifacts"]
            if artifact["path"].startswith("draft/")
        ]
        print("保守草稿已完成")
        print(f"Run: {manifest['run_id']}")
        print("生成的 artifacts:")
        for artifact_path in artifact_paths:
            print(f"- {artifact_path}")
        return 0

    if args.command == "review-run":
        try:
            run_dir = review_run(run_dir=Path(args.run))
        except (ReviewRunError, ResumeRunError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        artifact_paths = [
            artifact["path"]
            for artifact in manifest["artifacts"]
            if artifact["path"].startswith("review/") or artifact["path"].startswith("verify/")
        ]
        print("审查和验证已完成")
        print(f"Run: {manifest['run_id']}")
        print("生成的 artifacts:")
        for artifact_path in artifact_paths:
            print(f"- {artifact_path}")
        return 0

    if args.command == "finalize-run":
        try:
            run_dir = finalize_run(run_dir=Path(args.run))
        except (FinalizeRunError, ResumeRunError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Finalize run completed: {run_dir}")
        print("最终交付已完成。")
        print("生成的 artifacts:")
        print("- revision_plan.json")
        print("- revised/full_draft.md")
        print("- revised/change_log.md")
        print("- final/final_report.md")
        print("- final/delivery_summary.md")
        print("Status: finalized_with_open_items")
        return 0

    if args.command == "learning-run":
        try:
            run_dir = learning_run(run_dir=Path(args.run))
        except (LearningRunError, ResumeRunError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Learning run completed: {run_dir}")
        print("learning artifacts 已生成。")
        print("生成的 artifacts:")
        print("- trace/session_trace.jsonl")
        print("- trace/hitl_decisions.jsonl")
        print("- learning/run_summary.md")
        print("- learning/reusable_patterns.md")
        print("- learning/candidate_profile_update.yaml")
        print("- learning/candidate_skill_patch.md")
        print("- learning/promotion_report.md")
        print("Status: completed_with_candidate_updates_proposed")
        return 0

    if args.command == "resume-run":
        try:
            run_dir = resume_run(run_dir=Path(args.run))
        except ResumeRunError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Resumed run: {run_dir}")
        print("断点续写已完成。")
        print("Status: completed")
        print("说明：completed 仅表示 deterministic engine lifecycle 完成，不表示 professional approval。")
        return 0

    if args.command == "record-hitl":
        affected_sections = [section.strip() for section in args.affected_sections.split(",") if section.strip()]
        try:
            record = record_hitl(
                run_dir=Path(args.run),
                stage=args.stage,
                decision=args.decision,
                comment=args.comment,
                affected_sections=affected_sections,
                next_action=args.next_action,
            )
        except LearningRunError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print("HITL decision recorded")
        print("人工确认记录已写入。")
        print(f"Run: {record['run_id']}")
        print(f"Stage: {record['stage']}")
        print(f"Decision: {record['decision']}")
        return 0

    if args.command == "prepare-stage-review":
        try:
            result = prepare_stage_review(run_dir=Path(args.run), stage=args.stage)
        except StageReviewError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print("Stage review package prepared")
        print(f"Run: {result['run_id']}")
        print(f"Stage: {result['stage']}")
        print("Generated artifacts:")
        for artifact_path in result["artifacts"]:
            print(f"- {artifact_path}")
        print("Status: prepared_for_claude_review")
        print("Note: this is not professional approval and does not modify stage artifacts.")
        return 0

    if args.command == "validate-stage-review":
        try:
            report = validate_stage_review(
                run_dir=Path(args.run),
                stage=args.stage,
                issues_file=Path(args.issues_file) if args.issues_file else None,
            )
        except StageReviewError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print("Stage review issues validated")
        print(f"Run: {report['run_id']}")
        print(f"Stage: {report['stage']}")
        print(f"Status: {report['status']}")
        print(f"Report: stage_reviews/{report['stage']}/validation_report.json")
        print("Note: validation is not professional approval and does not apply fixes.")
        return 0

    if args.command == "record-stage-review-decision":
        try:
            record_stage_review_decision(
                run_dir=Path(args.run),
                stage=args.stage,
                decision=args.decision,
                notes=args.notes,
                decided_by=args.decided_by,
            )
        except StageReviewError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Recorded stage review gate decision: {args.decision}")
        print("Scope: stage_review_gate_only")
        print("This is not professional approval.")
        return 0

    if args.command == "check-stage-review-gate":
        try:
            result = check_stage_review_gate(run_dir=Path(args.run), stage=args.stage)
        except StageReviewError as exc:
            print(f"Stage review gate check failed for {args.stage}: {exc}", file=sys.stderr)
            return 1

        print(f"Stage review gate check passed for {result['stage']}.")
        print(f"Decision: {result['decision']}")
        print("Scope: stage_review_gate_only")
        print("This does not indicate professional approval.")
        return 0

    if args.command == "write-run":
        try:
            run_dir = write_run(task_file=Path(args.task), runs_dir=Path(args.runs_dir))
        except WriteRunError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print("写作流程已完成")
        print(f"Run: {run_dir}")
        print("Status: completed_with_candidate_updates_proposed")
        print("生成的 artifacts:")
        print("- final/final_report.md")
        print("- final/delivery_summary.md")
        print("- trace/session_trace.jsonl")
        print("- trace/hitl_decisions.jsonl")
        print("- learning/run_summary.md")
        print("- learning/candidate_profile_update.yaml")
        print("- learning/candidate_skill_patch.md")
        print("- learning/promotion_report.md")
        return 0

    if args.command == "profile-from-spec":
        from .document_types.spec_profile_generator import generate_profile_from_spec

        try:
            result = generate_profile_from_spec(
                spec_path=Path(args.spec),
                output_dir=Path(args.output_dir),
                force=args.force,
                dry_run=args.dry_run,
                no_skeletons=args.no_skeletons,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        if not result.success:
            print("Profile-from-spec failed", file=sys.stderr)
            for blocker in result.promotion_blockers:
                print(f"- {blocker}", file=sys.stderr)
            return 1

        print("candidate profile package 已生成")
        print(f"Output: {result.output_dir}")
        print(f"Profile: {result.manifest['generated_profile_path']}")
        print("Status: candidate/inactive")
        return 0

    if args.command == "correction-harvest":
        from .corrections.harvester import CorrectionHarvestError, harvest_corrections

        try:
            result = harvest_corrections(
                run_dir=Path(args.run_dir),
                corrections_path=Path(args.corrections),
                profile_path=Path(args.profile),
            )
        except CorrectionHarvestError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print("correction harvest 已完成")
        print(f"Run: {result['run_dir']}")
        print("生成的 artifacts:")
        print(f"- {result['correction_events_path']}")
        print(f"- {result['candidate_patch_path']}")
        print(f"- {result['candidate_eval_case_path']}")
        print("- learning/profile_promotion_report.json")
        print("- learning/profile_promotion_report.md")
        print("Status: blocked_pending_eval_or_approval")
        return 0

    if args.command == "profile-promote":
        from .corrections.promotion import promote_profile

        try:
            report = promote_profile(
                run_dir=Path(args.run_dir),
                candidate_patch_path=Path(args.candidate_patch),
                eval_report_path=Path(args.eval_report),
                approval_path=Path(args.approval) if args.approval else None,
                target_profile_path=Path(args.target_profile),
                output_dir=Path(args.output_dir),
                apply=args.apply,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print("profile promotion gate 已完成")
        print(f"Status: {report['status']}")
        print(f"Promoted: {str(report['promoted']).lower()}")
        print("生成的 artifacts:")
        print(f"- {Path(args.output_dir) / 'profile_promotion_report.json'}")
        print(f"- {Path(args.output_dir) / 'profile_promotion_report.md'}")
        if report["status"] in {"promoted", "dry_run_ready_to_promote"}:
            return 0
        return 1

    parser.print_help(sys.stderr)
    return 1
