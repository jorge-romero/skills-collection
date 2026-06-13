#!/usr/bin/env python3
"""
Analyze exploration areas and suggest what to explore next.

Reads all exploration/ area READMEs + _index.md, evaluates:
  - Current status of each area (status, priority, open questions)
  - Staleness (days since last update)
  - Dependency readiness (are dependencies saturated?)
  - Priority-ranked suggestions for what to do next

Usage:
  python suggest_next.py [exploration/ path]
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path


# ── Parsing (shared patterns with check_link_coherence.py) ──────────────

def find_areas(exploration_dir):
    """Discover all non-template area directories and parse their README.md."""
    areas = {}
    for entry in sorted(exploration_dir.iterdir()):
        if entry.is_dir() and entry.name != "_template":
            readme = entry / "README.md"
            if readme.exists():
                areas[entry.name] = _parse_area(readme)
            else:
                areas[entry.name] = {
                    "title": entry.name, "status": "unknown", "priority": "medium",
                    "last_updated": None, "links": {"depends_on": [], "feeds_into": [], "global_decisions": []},
                    "open_questions": 0, "ready_for_spec": "",
                }
    return areas


def _parse_frontmatter(content):
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    fm = {}
    for line in lines[1:end]:
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


def _parse_markdown_links(text):
    return re.findall(r"\[([^\]]+)\]\(\.\./([^/]+)/README\.md\)", text)


def _parse_section(content, heading):
    """Return the text of a ##-level section (empty string if missing)."""
    m = re.search(rf"^## {re.escape(heading)}\s*$", content, re.MULTILINE)
    if not m:
        return ""
    sec_start = m.end()
    next_sec = re.search(r"^## ", content[sec_start:], re.MULTILINE)
    return content[sec_start : sec_start + next_sec.start()].strip() if next_sec else content[sec_start:].strip()


def _count_open_questions(content):
    """Count bullet-point questions under ## Open Questions."""
    sec = _parse_section(content, "Open Questions")
    if not sec:
        return 0
    return sum(1 for line in sec.split("\n") if line.strip().startswith("- **"))


def _parse_area(readme_path):
    content = readme_path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(content)
    links = _parse_links_section(content)
    return {
        "title": fm.get("title", readme_path.parent.name),
        "status": fm.get("status", "unknown"),
        "priority": fm.get("priority", "medium"),
        "last_updated": fm.get("last-updated"),
        "links": links,
        "open_questions": _count_open_questions(content),
        "ready_for_spec": _parse_section(content, "Ready for Spec?"),
    }


def _parse_links_section(content):
    links = {"depends_on": [], "feeds_into": [], "global_decisions": []}
    m = re.search(r"^## Links\s*$", content, re.MULTILINE)
    if not m:
        return links
    sec_start = m.end()
    next_sec = re.search(r"^## ", content[sec_start:], re.MULTILINE)
    sec_text = content[sec_start : sec_start + next_sec.start()] if next_sec else content[sec_start:]
    for line in sec_text.split("\n"):
        line = line.strip()
        if line.startswith("- **Depends on:**"):
            links["depends_on"] = _parse_markdown_links(line)
        elif line.startswith("- **Feeds into:**"):
            links["feeds_into"] = _parse_markdown_links(line)
        elif line.startswith("- **Global decisions:**"):
            links["global_decisions"] = _parse_markdown_links(line)
    return links


# ── Analysis ────────────────────────────────────────────────────────────

_PRIORITY_SCORE = {"high": 0, "medium": 1, "low": 2}


def days_since(date_str):
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except ValueError:
        return None


def all_deps_saturated(slug, areas):
    """Check if every area this one depends on is saturated."""
    deps = areas[slug]["links"]["depends_on"]
    if not deps:
        return True
    for _, target in deps:
        if target not in areas:
            return False
        if areas[target]["status"] != "saturated":
            return False
    return True


def analyze(areas):
    """Return suggestions sorted by priority + staleness."""
    slugs = set(areas.keys())
    suggestions = []

    for slug, area in areas.items():
        status = area["status"]
        pri = _PRIORITY_SCORE.get(area["priority"], 99)
        ds = days_since(area["last_updated"])
        deps_ready = all_deps_saturated(slug, areas)
        has_qs = area["open_questions"] > 0

        if status == "in-progress" and has_qs:
            urgency = pri
            suggestions.append({
                "slug": slug,
                "title": area["title"],
                "action": "continue",
                "reason": f"Has {area['open_questions']} open question(s) that need resolution",
                "urgency": urgency,
            })

        if status == "in-progress" and not has_qs and ds is not None and ds > 14:
            urgency = pri + 1
            suggestions.append({
                "slug": slug,
                "title": area["title"],
                "action": "review",
                "reason": f"No open questions but not updated in {ds} days — check if it should be saturated",
                "urgency": urgency,
            })

        if status == "not-started":
            urgency = pri
            suggestions.append({
                "slug": slug,
                "title": area["title"],
                "action": "start",
                "reason": "Not yet explored",
                "urgency": urgency,
            })

        if status == "saturated":
            urgency = pri + 2
            suggestions.append({
                "slug": slug,
                "title": area["title"],
                "action": "spec",
                "reason": "Ready for a change proposal",
                "urgency": urgency,
            })

    suggestions.sort(key=lambda s: (s["urgency"], s["slug"]))

    # Rank by priority/action
    ranked = []
    seen = set()
    priority_order = {"continue": 0, "start": 1, "spec": 2, "review": 3}
    suggestions.sort(key=lambda s: (priority_order.get(s["action"], 99), s["urgency"], s["slug"]))
    for i, sug in enumerate(suggestions):
        if sug["slug"] not in seen:
            seen.add(sug["slug"])
            sug["rank"] = len(ranked) + 1
            ranked.append(sug)

    return ranked


def build_area_rows(areas):
    """Build table data for status overview."""
    rows = []
    for slug in sorted(areas.keys()):
        a = areas[slug]
        ds = days_since(a["last_updated"])
        ds_str = f"{ds}d" if ds is not None else "-"
        rows.append({
            "slug": slug,
            "title": a["title"],
            "status": a["status"],
            "priority": a["priority"],
            "last_updated": a["last_updated"] or "-",
            "days_since": ds_str,
            "open_questions": a["open_questions"],
            "ready_for_spec": "Yes" if a["ready_for_spec"] and "yes" in a["ready_for_spec"].strip().lower() else "Not yet",
        })
    return rows


# ── Output ──────────────────────────────────────────────────────────────

def print_table(rows):
    """Print a human-readable table of area status."""
    sep = "─" * 80
    header = f"{'Area':<20} {'Status':<14} {'Pri':<5} {'Updated':<12} {'Age':<6} {'Qs':<4}  Ready"
    print(f"\n{'Exploration Status Dashboard':^80}")
    print(sep)
    print(header)
    print(sep)
    for r in rows:
        print(f"{r['slug']:<20} {r['status']:<14} {r['priority']:<5} {r['last_updated']:<12} {r['days_since']:<6} {r['open_questions']:<4}  {r['ready_for_spec']}")
    print(sep)
    total = len(rows)
    by_status = {}
    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    status_line = "  ".join(f"{v} {k}" for k, v in sorted(by_status.items()))
    print(f"Total: {total} area(s)  |  {status_line}")
    print()


def print_suggestions(suggestions, areas):
    """Print ranked suggestions with context."""
    if not suggestions:
        print("No suggestions — all areas are resolved or dropped.")
        return

    print(f"{'Suggested Next Steps':^80}")
    print("─" * 80)

    for i, sug in enumerate(suggestions):
        a = areas[sug["slug"]]
        icon = {"continue": "→", "start": "▶", "spec": "◆", "review": "?"}.get(sug["action"], "·")
        print(f"\n{icon}  #{sug['rank']}: {sug['action'].upper()} — {sug['title']} ({sug['slug']})")
        print(f"   Status: {a['status']}, priority: {a['priority']}")
        if a["open_questions"] > 0:
            print(f"   Open questions: {a['open_questions']}")
        ds = days_since(a["last_updated"])
        if ds is not None:
            print(f"   Last updated: {ds} day(s) ago")
        print(f"   Why: {sug['reason']}")

    print()


def main():
    exploration_path = sys.argv[1] if len(sys.argv) > 1 else "./exploration/"
    exploration_dir = Path(exploration_path)

    if not exploration_dir.exists():
        print(f"Exploration directory '{exploration_dir}' does not exist.", file=sys.stderr)
        print("Create one with the structured-explore skill ('exploration/' in your project root).", file=sys.stderr)
        sys.exit(0)

    areas = find_areas(exploration_dir)

    if not areas:
        print("No exploration areas found.")
        return

    # Build analysis
    rows = build_area_rows(areas)
    suggestions = analyze(areas)

    # Print human-readable
    print_table(rows)
    print_suggestions(suggestions, areas)

    # JSON output for programmatic use
    result = {
        "analysis_date": str(date.today()),
        "exploration_dir": str(exploration_dir),
        "areas": [
            {
                "slug": r["slug"],
                "title": r["title"],
                "status": r["status"],
                "priority": r["priority"],
                "last_updated": r["last_updated"],
                "days_since_update": r["days_since"],
                "open_question_count": r["open_questions"],
                "ready_for_spec": r["ready_for_spec"],
            }
            for r in rows
        ],
        "suggestions": [
            {
                "rank": s["rank"],
                "action": s["action"],
                "slug": s["slug"],
                "title": s["title"],
                "reason": s["reason"],
            }
            for s in suggestions
        ],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
