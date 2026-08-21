"""Command-line interface for CineOps."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .evidence import build_evidence_summary
from .impact import compare_ledgers
from .report import render_demo_report, render_project_report
from .validator import (
    load_json,
    summarize,
    validate_project,
    validate_release_gate,
)


def _template_dir() -> Path:
    return Path(__file__).with_name("templates")


def command_init(destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    created = 0
    for source in _template_dir().glob("*.json"):
        target = destination / source.name
        if target.exists():
            print(f"skip {target} (already exists)")
            continue
        shutil.copyfile(source, target)
        print(f"create {target}")
        created += 1
    print(f"Initialized {created} artifact(s) in {destination}")
    return 0


def command_validate(root: Path, output_json: bool) -> int:
    findings = validate_project(root)
    counts = summarize(findings)
    if output_json:
        print(json.dumps({"findings": [finding.__dict__ for finding in findings], "summary": counts}, indent=2))
    else:
        for finding in findings:
            print(finding.render())
        print(f"Summary: {counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info")
    return 1 if counts["error"] else 0


def command_gate(root: Path, output_json: bool) -> int:
    findings = validate_release_gate(root)
    counts = summarize(findings)
    if output_json:
        report = {
            "release_ready": counts["error"] == 0,
            "findings": [finding.__dict__ for finding in findings],
            "summary": counts,
        }
        print(json.dumps(report, indent=2))
    else:
        for finding in findings:
            print(finding.render())
        status = "READY" if counts["error"] == 0 else "NOT READY"
        print(f"Release gate: {status} ({counts['error']} error(s), {counts['warning']} warning(s))")
    return 1 if counts["error"] else 0


def command_impact(before: Path, after: Path) -> int:
    report = compare_ledgers(load_json(before), load_json(after))
    print(json.dumps(report, indent=2))
    return 0


def command_evidence(root: Path, output: Path | None) -> int:
    report = build_evidence_summary(root)
    serialized = json.dumps(report, indent=2) + "\n"
    if output is None:
        print(serialized, end="")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(serialized, encoding="utf-8")
        print(f"Wrote privacy-safe evidence summary to {output}")
    return 0


def command_report(root: Path, output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_project_report(root), encoding="utf-8")
    print(f"Wrote visual production report to {output}")
    return 0


def command_demo(destination: Path) -> int:
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        print(f"Demo destination must be empty: {destination}", file=sys.stderr)
        return 2
    destination.mkdir(parents=True, exist_ok=True)
    source_root = Path(__file__).with_name("demo")
    before = destination / "before"
    after = destination / "after"
    shutil.copytree(source_root / "before", before)
    shutil.copytree(source_root / "after", after)
    report = destination / "cineops-demo.html"
    report.write_text(render_demo_report(before, after), encoding="utf-8")
    print("CineOps demo created:")
    print(f"  before: {before}")
    print(f"  after:  {after}")
    print(f"  report: {report}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cineops", description="Validate AI film production artifacts")
    parser.add_argument("--version", action="version", version=f"cineops {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="create a blank CineOps project")
    init_parser.add_argument("destination", type=Path)
    validate_parser = subparsers.add_parser("validate", help="validate a CineOps project")
    validate_parser.add_argument("project", type=Path)
    validate_parser.add_argument("--json", action="store_true", dest="output_json")
    gate_parser = subparsers.add_parser("gate", help="enforce release readiness for every shot")
    gate_parser.add_argument("project", type=Path)
    gate_parser.add_argument("--json", action="store_true", dest="output_json")
    evidence_parser = subparsers.add_parser("evidence", help="export a privacy-safe pilot summary")
    evidence_parser.add_argument("project", type=Path)
    evidence_parser.add_argument("--output", "-o", type=Path)
    impact_parser = subparsers.add_parser("impact", help="compare two continuity ledgers")
    impact_parser.add_argument("before", type=Path)
    impact_parser.add_argument("after", type=Path)
    report_parser = subparsers.add_parser("report", help="write a self-contained visual readiness report")
    report_parser.add_argument("project", type=Path)
    report_parser.add_argument("--output", "-o", type=Path, default=Path("cineops-report.html"))
    demo_parser = subparsers.add_parser("demo", help="create a zero-configuration before/after demo")
    demo_parser.add_argument("destination", type=Path, nargs="?", default=Path("cineops-demo"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        return command_init(args.destination)
    if args.command == "validate":
        return command_validate(args.project, args.output_json)
    if args.command == "gate":
        return command_gate(args.project, args.output_json)
    if args.command == "evidence":
        return command_evidence(args.project, args.output)
    if args.command == "impact":
        return command_impact(args.before, args.after)
    if args.command == "report":
        return command_report(args.project, args.output)
    if args.command == "demo":
        return command_demo(args.destination)
    return 2


if __name__ == "__main__":
    sys.exit(main())
