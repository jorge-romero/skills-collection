---
name: structured-explore
description: >-
  Explore a complex problem and capture findings into structured per-area
  exploration directories. Use when the user wants to investigate a topic,
  research options, think through a design, gather information before committing
  to a solution, or decompose a large problem into smaller exploration areas.
  This skill is for investigating problems, clarifying requirements, exploring
  solution spaces, and organizing findings into a persistent, machine-readable
  structure — NOT for implementing code or writing proposals. Trigger whenever
  the user expresses intent to explore, investigate, research, or think through
  something, even if they don't explicitly ask for structure. If the
  exploration/ directory exists, always prefer this skill over raw conversation.
  The structured output feeds directly into specification later.
license: MIT
---

# Structured Exploration

Exploration mode with persistent output. Think freely like openspec-explore, but
when the user asks to explore or capture, write findings into the `exploration/`
directory: one directory per area with a structured `README.md` and freeform
`notes.md`.

## The Stance

Same as openspec-explore — curious, visual, adaptive, patient:

- **Curious, not prescriptive** — Ask questions that emerge naturally, don't follow a script
- **Open threads, not interrogations** — Surface multiple directions, let the user follow
- **Visual** — Use ASCII diagrams when they'd clarify thinking
- **Grounded** — Read the codebase and existing exploration areas, don't just theorize
- **No rushing** — Let the shape of the problem emerge

## Capture Permission Model

The skill has two modes depending on how the user phrases their request:

**Explore Mode** (user is vague, wondering, or exploring freely):
The user says things like "what about...", "I'm wondering...", "how would we handle..."
→ Explore with diagrams and questions. Offer to capture when insights crystallize.
Ask: "Want me to capture this in the exploration dir?"

**Capture Mode** (user expresses intent to explore and capture):
The user says things like "let me explore [topic] properly", "capture these findings",
"record this as an exploration area", "let me think through [topic] and document it"
→ Explore AND capture. The user is literally asking you to produce structured docs.
Do NOT just offer — they already said yes. Create the area, write the findings,
update the dashboard. This is following instructions, not auto-capturing.

Examples of capture-intent phrases:
- "Let me explore [X] properly" — the word "properly" signals they want structure
- "Capture these findings" — explicit instruction
- "Record this as an exploration area" — explicit instruction
- "I want to think through [X] and document it" — intent to produce docs
- "Let me investigate [X] systematically" — wants structured output
- "Explore [X] and put it in the structure" — explicit reference

If unsure, default to Explore Mode (offer first).

## The Exploration Structure

```
exploration/
  _index.md              ← dashboard, session log, cross-cutting decisions
  _template/             ← starter files for new areas
    README.md            ← template with YAML frontmatter + sections
    notes.md             ← empty scratch file
  <area-slug>/
    README.md            ← structured findings (fixed template)
    notes.md             ← raw notes, links, research
```

### _index.md Sections

| Section | Purpose | Update When |
|---------|---------|-------------|
| Status Dashboard | Table of all areas: id, status, priority, last updated | After creating an area, changing status, or updating priority |
| Session Log | Chronological table of exploration sessions | After each session ends or at natural break points |
| Cross-Cutting Decisions | Decisions affecting multiple areas | When a decision spans 2+ areas |
| Core Vision | Project-level context (top of file) | Rarely — when the project's direction changes |

### Per-Area README.md Template

Every area directory's `README.md` uses this structure:

```markdown
---
id: area-slug
title: Human-Readable Title
status: not-started    # not-started | in-progress | saturated | dropped
priority: medium       # high | medium | low
last-updated: YYYY-MM-DD
---

## Summary
One-paragraph description of what this area covers.

## Scope
What's in and (explicitly) what's out.

## Findings
Key learnings and design decisions. Each finding should be
self-contained — someone should understand it without reading
other docs. Use subheadings for distinct findings.

## Open Questions
Still-unresolved items. For each: what makes it hard, any
partial answers, what input is needed to resolve it.

## Links
- **Depends on:** areas whose findings this builds on
- **Feeds into:** areas that build on this
- **Global decisions:** cross-cutting decisions in `_index.md` that constrain this area

## Ready for Spec?
What's missing before this can become a change proposal.
```

## Status Lifecycle

```
                ┌─────────┐
                │  not    │
                │ started │
                └────┬────┘
               ┌─────┴──────┐
               ▼             ▼
          ┌──────────┐  ┌──────────┐
          │in-progress│  │ dropped  │
          └─────┬────┘  └──────────┘
                │
                ▼
          ┌──────────┐
          │ saturated │──► change proposal
          └──────────┘
```

- **not-started**: Area identified, not yet explored
- **in-progress**: Actively being explored
- **saturated**: Explored enough to write a change proposal
- **dropped**: Decided not to pursue

## Bootstrap: First Time Setup

If `exploration/` does not exist in the project root, create it before doing
anything else. This is a one-time setup.

Create these files:

**exploration/_index.md:**
```markdown
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
- **"Saturated"** means exploration is deep enough to write a change proposal.
- **Links are bidirectional.** When you update findings in one area, check Links sections of related areas.
- **Sessions go in the session log.** After each exploration session, add a row above.

## How to Use

1. Pick an area from the dashboard (prefer `in-progress` or high-priority `not-started`).
2. Read its `README.md` for context and open questions.
3. Explore. Update Findings and Open Questions as you go.
4. Set status to `saturated` when exploration is sufficient for a spec.
5. Mark `dropped` if you decide not to pursue.
6. When saturated, use OpenSpec to write a change spec.
```

**exploration/_template/README.md:**
```markdown
---
id: area-slug
title: Human-Readable Title
status: not-started
priority: medium
last-updated: YYYY-MM-DD
---

## Summary

One-paragraph description of what this area covers.

## Scope

What's in and (explicitly) what's out.

## Findings

Key learnings, design decisions, crystallized ideas.

### Finding 1: ...

### Finding 2: ...

## Open Questions

- **Q1:** ... — What makes it hard, partial answers, what input is needed.

## Links

- **Depends on:** areas whose findings this builds on
- **Feeds into:** areas that build on this
- **Global decisions:** cross-cutting decisions in `_index.md` that constrain this area

## Ready for Spec?

What's missing before this can become a change proposal.
```

**exploration/_template/notes.md:**
```markdown
# Raw Notes — Area Name

URLs, quotes, half-formed ideas, research links, etc.
```

After creating the bootstrap files, proceed with the Capture or Explore workflow below.

## Workflow: Capture Mode

When the user expresses capture intent (see permission model above):

### Step 1: Read Context

Before anything else, read these to understand what already exists:
1. `exploration/_index.md` — dashboard, cross-cutting decisions, session log
2. `exploration/_template/README.md` — template structure

If either file is missing, run the bootstrap setup first.

### Step 2: Check for Overlaps

Read existing area READMEs that might relate to the topic. If an area already
covers similar ground, offer to update it instead of creating a new one.
List the overlap clearly so the user can decide.

### Step 3: Explore the Problem

Ground the exploration in the existing codebase and architecture. Use:
- ASCII diagrams for system relationships, flows, comparisons
- References to actual schema, API endpoints, code
- Questions that probe assumptions and edge cases

### Step 4: Capture into Structure

Create or update the area directory:

**For a new area:**
```
cp -r exploration/_template/ exploration/<slug>/
```

Then fill the README:
1. YAML frontmatter: id, title, status=in-progress, priority, last-updated
2. **Summary** — one paragraph describing what this area covers
3. **Scope** — what's in and explicitly what's out
4. **Findings** — each finding as a self-contained subsection with rationale
5. **Open Questions** — unresolved items with partial answers if any
6. **Links** — bidirectional connections using canonical relative paths. Always
   check existing area READMEs to see what's relevant. Use markdown links with
   relative paths (e.g., `[Task Board Data Model](../task-board-data-model/README.md)`),
   not just human-readable names. Include:
   - **Depends on:** areas whose findings this builds on
   - **Feeds into:** areas that could build on this
   - **Global decisions:** at least one cross-cutting decision from `_index.md` that
     constrains this area
7. **Ready for Spec?** — what's missing before writing a change proposal

Create `notes.md` with raw thoughts, URLs, code snippets, references.

### Step 5: Update _index.md

1. Add a row to the **Status Dashboard** (for new areas)
2. Add a row to the **Session Log** (for this session)
3. If a cross-cutting decision emerged, add it to **Cross-Cutting Decisions**

Always update `_index.md` before finishing — a new area without a dashboard entry
is invisible. A session without a log entry is lost.

## Workflow: Explore Mode

When the user is exploring freely (no capture intent):

1. Read relevant existing areas to ground the discussion
2. Use diagrams, comparisons, open questions
3. When insights crystallize (design decisions, new areas, open questions identified),
   offer to capture: "Want me to capture this in the exploration dir?"
4. Wait for the user's response before creating files

## Maintaining an Existing Area

When the user asks to explore within an existing area, or findings update one:

1. Read the area's README.md and notes.md
2. Explore the new angle
3. Offer to update: add findings, refine open questions, adjust status
4. If the user agrees, edit the README and update `last-updated` in frontmatter

## Nuanced Actions

### Reorganizing Areas
When 4+ areas have reached `saturated` or `dropped`, suggest reorganizing into
`active/`, `saturated/`, and `dropped/` subfolders. Only suggest when the flat
list feels unwieldy.

### Splitting an Area
If exploration reveals two independent sub-threads, suggest splitting. Create one
area per sub-thread, link them bidirectionally, set the original to `dropped`
with a note pointing to the split.

### Merging Areas
If two areas overlap heavily, suggest merging. Pick one survivor, move findings
there, set the other to `dropped` with a redirect link.

## Guardrails

- **Don't implement** — Never write application code. Creating exploration files
  is capturing thinking, not implementing. If the user asks to implement, suggest
  finishing exploration and using a change proposal workflow instead.
- **Don't force structure in Explore Mode** — Let exploration happen freely, offer
  capture when insights crystallize.
- **Do capture in Capture Mode** — When the user says "explore X properly" or
  "capture X", they're asking for structured output. Create it.
- **Do read related areas first** — New areas should always link to existing ones.
  Stale or missing links are worse than no links.
- **Do keep READMEs polished** — notes.md can be messy, but README.md is the
  public face of an area.
- **Do update _index.md** — A new area without a dashboard entry is invisible.
- **Don't create changes** — That's the next step, not this skill's job.
