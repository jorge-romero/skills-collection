# Exploration Index

**Project:** [Project Name]
**Started:** [YYYY-MM-DD]
**Context:** Brief context about what this project is exploring.

## Status Dashboard

| Area | Status | Priority | Last Updated |
|------|--------|----------|-------------|

## Session Log

| Date | Areas Touched | Key Outcomes |
|------|--------------|--------------|

## Cross-Cutting Decisions

| Decision | Rationale | Affects | Date |
|----------|-----------|---------|------|

## Conventions

- **Creating a new area:** Copy `_template/` to a new directory with a short descriptive slug.
- **Status transitions:** `not-started → in-progress → saturated → spec`. Exceptions: `not-started → dropped`, `saturated → dropped`.
- **"Saturated"** means exploration is deep enough to write an OpenSpec change.
- **Links are bidirectional.** When you update findings in one area, check Links sections of related areas.
- **Sessions go in the session log.** After each exploration session, add a row above.

## How to Use

1. Pick an area from the dashboard (prefer `in-progress` or high-priority `not-started`).
2. Read its `README.md` for context and open questions.
3. Explore. Update Findings and Open Questions as you go.
4. Set status to `saturated` when exploration is sufficient for a spec.
5. Mark `dropped` if you decide not to pursue.
6. When saturated, use OpenSpec to write a change spec.
