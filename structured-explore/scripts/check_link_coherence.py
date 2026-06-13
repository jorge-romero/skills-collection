#!/usr/bin/env python3
"""
Check link coherence across structured-explore areas.

Reads all exploration/ area READMEs + _index.md, checks:
  - Dangling links (target slug doesn't match any area directory)
  - Bidirectional consistency (A→B implies B→A for Depends on / Feeds into)
  - Status coherence (depending on a dropped/not-started area)
  - Orphan areas (on disk but not in dashboard)

Usage:
  python check_link_coherence.py [exploration/ path]
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path


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
                    "title": entry.name,
                    "status": "unknown",
                    "links": {"depends_on": [], "feeds_into": [], "global_decisions": []},
                }
    return areas


def _parse_frontmatter(content):
    """Extract simple YAML frontmatter between --- delimiters."""
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
    frontmatter = {}
    for line in lines[1:end]:
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    return frontmatter


def _parse_markdown_links(text):
    """Extract (label, slug) from ``[Label](../slug/README.md)`` links."""
    return re.findall(r"\[([^\]]+)\]\(\.\./([^/]+)/README\.md\)", text)


def _parse_links_section(content):
    """Parse the ``## Links`` section for Depends on / Feeds into / Global decisions."""
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


def _parse_area(readme_path):
    """Parse a single area README.md into metadata + link structure."""
    content = readme_path.read_text(encoding="utf-8")
    frontmatter = _parse_frontmatter(content)
    links = _parse_links_section(content)
    return {
        "title": frontmatter.get("title", readme_path.parent.name),
        "status": frontmatter.get("status", "unknown"),
        "links": links,
    }


def _parse_index_dashboard(exploration_dir):
    """Return a set of area slugs or titles mentioned in the Status Dashboard table."""
    index_path = exploration_dir / "_index.md"
    if not index_path.exists():
        return set()
    content = index_path.read_text(encoding="utf-8")
    m = re.search(r"^## Status Dashboard\s*$", content, re.MULTILINE)
    if not m:
        return set()
    sec_start = m.end()
    next_sec = re.search(r"^## ", content[sec_start:], re.MULTILINE)
    sec_text = content[sec_start : sec_start + next_sec.start()] if next_sec else content[sec_start:]
    table_lines = [l for l in sec_text.strip().split("\n") if l.startswith("|")]

    result = set()
    for line in table_lines:
        slugs = re.findall(r"\]\(\.\./([^/]+)/README\.md\)", line)
        if slugs:
            result.update(slugs)
        else:
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 1 and cells[1] and "Area" not in cells[1] and "---" not in line:
                result.add(cells[1])
    return result


def check_coherence(areas, dashboard_areas):
    """Return a list of issue dicts found in the area graph."""
    issues = []
    slugs = set(areas.keys())

    for slug, area in areas.items():
        links = area["links"]

        for label, target in links["feeds_into"]:
            if target not in slugs:
                issues.append({
                    "area": slug,
                    "category": "dangling",
                    "description": f"Feeds into '{target}' ({label}) does not exist as an exploration area.",
                })

        for label, target in links["depends_on"]:
            if target not in slugs:
                issues.append({
                    "area": slug,
                    "category": "dangling",
                    "description": f"Depends on '{target}' ({label}) does not exist as an exploration area.",
                })

        for label, target in links["feeds_into"]:
            if target in areas:
                tdeps = [s for _, s in areas[target]["links"]["depends_on"]]
                if slug not in tdeps:
                    issues.append({
                        "area": slug,
                        "category": "bidirectional",
                        "description": f"Feeds into '{target}' but {target}/README.md does not list '{slug}' in Depends on.",
                    })

        for label, target in links["depends_on"]:
            if target in areas:
                tfeeds = [s for _, s in areas[target]["links"]["feeds_into"]]
                if slug not in tfeeds:
                    issues.append({
                        "area": slug,
                        "category": "bidirectional",
                        "description": f"Depends on '{target}' but {target}/README.md does not list '{slug}' in Feeds into.",
                    })

        for label, target in links["depends_on"]:
            if target in areas:
                ts = areas[target]["status"]
                if ts in ("dropped", "not-started"):
                    issues.append({
                        "area": slug,
                        "category": "status",
                        "description": f"Depends on '{target}' (status: {ts}) — its findings may not be stable.",
                    })

    for slug in areas:
        if slug not in dashboard_areas:
            title = areas[slug]["title"]
            matched = any(title in d for d in dashboard_areas) if dashboard_areas else False
            if not matched:
                issues.append({
                    "area": slug,
                    "category": "orphan",
                    "description": f"Area '{slug}' exists on disk but is not listed in _index.md Status Dashboard.",
                })

    return issues


def main():
    exploration_path = sys.argv[1] if len(sys.argv) > 1 else "./exploration/"
    exploration_dir = Path(exploration_path)

    if not exploration_dir.exists():
        result = {
            "checks_run_at": str(date.today()),
            "exploration_dir": str(exploration_dir),
            "areas_scanned": [],
            "issues": [],
        }
        print(json.dumps(result, indent=2))
        return

    areas = find_areas(exploration_dir)
    dashboard_areas = _parse_index_dashboard(exploration_dir)
    issues = check_coherence(areas, dashboard_areas)

    result = {
        "checks_run_at": str(date.today()),
        "exploration_dir": str(exploration_dir),
        "areas_scanned": sorted(areas.keys()),
        "issues": issues,
    }

    print(json.dumps(result, indent=2))

    if issues:
        print(f"\n{'⚠'}  Found {len(issues)} issue(s):", file=sys.stderr)
        for iss in issues:
            print(f"  [{iss['category']}] {iss['area']}: {iss['description']}", file=sys.stderr)
    else:
        print("\n{'✓'} No coherence issues found.", file=sys.stderr)


if __name__ == "__main__":
    main()
