"""Self-contained visual reports for CineOps projects."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .evidence import build_evidence_summary
from .validator import Finding, summarize, validate_project, validate_release_gate


def _status_label(release_ready: bool) -> str:
    return "READY" if release_ready else "NOT READY"


def _finding_rows(findings: list[Finding]) -> str:
    if not findings:
        return '<div class="empty">No structural findings. The handoff is coherent.</div>'
    return "".join(
        (
            f'<article class="finding {escape(item.severity)}">'
            f'<span class="severity">{escape(item.severity.upper())}</span>'
            f'<div><strong>{escape(item.code)}</strong>'
            f'<small>{escape(item.path)}</small>'
            f'<p>{escape(item.message)}</p></div></article>'
        )
        for item in findings
    )


def _project_panel(root: Path, label: str) -> str:
    evidence = build_evidence_summary(root)
    findings = validate_project(root)
    gate_findings = validate_release_gate(root)
    counts = summarize(findings)
    release_ready = summarize(gate_findings)["error"] == 0
    artifacts = evidence["artifact_counts"]
    decisions = evidence["review_decisions"]
    return f"""
      <section class="project-panel">
        <div class="panel-heading">
          <div>
            <span class="eyebrow">{escape(label)}</span>
            <h2>{_status_label(release_ready)}</h2>
          </div>
          <span class="status {'ready' if release_ready else 'blocked'}">
            {'Release ready' if release_ready else 'Release blocked'}
          </span>
        </div>
        <div class="metrics">
          <div><strong>{artifacts['shots']}</strong><span>shots</span></div>
          <div><strong>{artifacts['reviews']}</strong><span>reviews</span></div>
          <div><strong>{counts['error']}</strong><span>errors</span></div>
          <div><strong>{counts['warning']}</strong><span>warnings</span></div>
        </div>
        <div class="decision-row">
          <span>Ready {decisions.get('ready', 0)}</span>
          <span>Revise {decisions.get('revise', 0)}</span>
          <span>Blocked {decisions.get('blocked', 0)}</span>
        </div>
        <div class="findings">{_finding_rows(findings)}</div>
      </section>
    """


def _document(body: str, title: str, subtitle: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --ink: #f7f6ef; --muted: #aaa99f; --panel: #171918;
      --line: #30332f; --green: #77e49a; --red: #ff7b6b; --amber: #ffc85a; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; color: var(--ink); background:
      radial-gradient(circle at 8% 4%, #20382b 0, transparent 28rem),
      radial-gradient(circle at 92% 10%, #332719 0, transparent 24rem), #0c0e0d;
      font: 15px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}
    main {{ width: min(1180px, calc(100% - 36px)); margin: 0 auto; padding: 64px 0 80px; }}
    header {{ margin-bottom: 30px; animation: rise .55s ease-out both; }}
    .brand {{ color: var(--green); font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }}
    h1 {{ margin: 8px 0 4px; font-size: clamp(36px, 6vw, 72px); line-height: .98; letter-spacing: -.045em; }}
    header p {{ max-width: 720px; color: var(--muted); font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 18px; }}
    .project-panel {{ background: color-mix(in srgb, var(--panel) 94%, transparent); border: 1px solid var(--line);
      border-radius: 20px; padding: 24px; box-shadow: 0 24px 70px #0008; animation: rise .65s ease-out both; }}
    .project-panel:nth-child(2) {{ animation-delay: .1s; }}
    .panel-heading {{ display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; }}
    .eyebrow {{ color: var(--muted); text-transform: uppercase; letter-spacing: .12em; font-size: 12px; font-weight: 800; }}
    h2 {{ margin: 3px 0 0; font-size: 34px; letter-spacing: -.03em; }}
    .status {{ border-radius: 999px; padding: 7px 11px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .status.ready {{ color: #07170d; background: var(--green); }}
    .status.blocked {{ color: #210806; background: var(--red); }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 24px 0 12px; }}
    .metrics div {{ padding: 12px; border-radius: 12px; background: #0f1110; border: 1px solid #252825; }}
    .metrics strong {{ display: block; font-size: 24px; }}
    .metrics span, small {{ display: block; color: var(--muted); font-size: 12px; }}
    .decision-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }}
    .decision-row span {{ color: var(--muted); background: #232622; border-radius: 999px; padding: 5px 9px; font-size: 12px; }}
    .findings {{ display: grid; gap: 8px; }}
    .finding {{ display: grid; grid-template-columns: 68px 1fr; gap: 12px; border: 1px solid var(--line);
      border-radius: 12px; padding: 12px; background: #111312; }}
    .finding .severity {{ align-self: start; width: fit-content; padding: 3px 6px; border-radius: 6px;
      color: #160806; background: var(--red); font-size: 10px; font-weight: 900; letter-spacing: .08em; }}
    .finding.warning .severity {{ color: #201400; background: var(--amber); }}
    .finding.info .severity {{ color: #061711; background: #64d9c0; }}
    .finding p {{ margin: 4px 0 0; color: #d6d5ce; }}
    .empty {{ padding: 20px; border: 1px dashed #3f624a; border-radius: 12px; color: var(--green); background: #102017; }}
    footer {{ margin-top: 22px; color: var(--muted); font-size: 12px; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @media (max-width: 620px) {{ main {{ padding-top: 36px; }} .metrics {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">CineOps</div>
      <h1>{escape(title)}</h1>
      <p>{escape(subtitle)}</p>
    </header>
    <div class="grid">{body}</div>
    <footer>Generated locally by CineOps. This report does not load external scripts, fonts, or analytics.</footer>
  </main>
</body>
</html>
"""


def render_project_report(root: Path) -> str:
    return _document(
        _project_panel(root, "Production handoff"),
        "Production Readiness",
        "A deterministic view of artifact integrity, review coverage, and release-gate status.",
    )


def render_demo_report(before: Path, after: Path) -> str:
    return _document(
        _project_panel(before, "Before CineOps") + _project_panel(after, "After repair"),
        "Catch The Handoff",
        "The same one-shot handoff before and after its broken references, timing, state, and review coverage are repaired.",
    )
