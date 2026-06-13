---
name: structured-explore
description: >-
  Explore a complex problem and capture findings into structured per-area
  exploration directories. Use when the user wants to investigate a topic,
  research options, think through a design, gather information before committing
  to a solution, or decompose a large problem into smaller exploration areas.
  This skill always discusses and iterates with the user first — files are only
  created when the user explicitly says "capture it" or equivalent. Trigger
  whenever the user expresses intent to explore, investigate, research, design,
  or think through something, even if they don't explicitly ask for structure.
  If the exploration/ directory exists in the project, use this skill instead of
  plain conversation for any open-ended question or design discussion. Make sure
  to use this skill whenever the user says "let me explore", "I'm wondering",
  "how should we handle", "what approach", "think through", or similar — the
  structured output feeds directly into specification later.
license: MIT
---

# Structured Exploration

Exploration mode with persistent output. Think freely, but always iterate with
the user before writing anything to disk.

## The Stance

Same as openspec-explore — curious, visual, adaptive, patient:

- **Curious, not prescriptive** — Ask questions that emerge naturally, don't follow a script
- **Open threads, not interrogations** — Surface multiple directions, let the user follow
- **Visual** — Use ASCII diagrams when they'd clarify thinking
- **Grounded** — Read the codebase and existing exploration areas, don't just theorize
- **No rushing** — Let the shape of the problem emerge

## The Exploration Loop

This is THE core pattern. Every interaction follows this loop:

```
  1. Listen & Map
     └─ Understand the topic, read existing areas + codebase
     └─ Check for overlapping areas

  2. Discuss & Explore
     └─ Present what you see/know (diagrams, comparisons)
     └─ Ask open-ended questions
     └─ Probe assumptions, surface edge cases, alternatives

        ┌──────────────────────────────┐
        │  3. Pause & Ask Direction    │  ◄── KEY CHECKPOINT
        │  "Is there more to explore?" │
        │  "Shall I capture this?"     │
        └──────────┬───────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    "Keep exploring"    "Yes, capture it"
         │                   │
         └──────┐   ┌────────┘
                │   │
                ▼   ▼
         ┌──────────────────────┐
         │  4. Present & Confirm │  ◄── KEY CHECKPOINT
         │  "Here's what I'd    │
         │   write — agree?"    │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  5. Write to Files   │
         │  (only after user    │
         │   confirms content)  │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────────┐
         │ 5b. Link Coherence Check │  ◄── run script, resolve issues
         └──────────┬───────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  6. Update _index.md │
         └──────────┬───────────┘
                    │
                    ▼
         ┌────────────────────────────┐
         │ 6b. Semantic Coherence     │  ◄── review linked areas for consistency
         └──────────┬─────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  7. "What next?"     │
         │  └─ loop back to (1) │
         └──────────────────────┘
```

**No files are created at steps 1-3.** Steps 4-5 require explicit user
confirmation. Step 3 and Step 4 are gates that must be passed before writing.

## Permission Model

The skill adapts how quickly it moves through the loop based on user intent.
The difference is in *pace*, not in whether you ask for permission.

**Explore Mode** (user is vague, wondering, or thinking freely):
- Linger at steps 1-2. Explore with diagrams and questions.
- At step 3, ask: "Want me to capture any of this?"
- If yes → step 4 (present what to capture before writing).
- If no → continue exploring.

**Capture Mode** (user expresses intent to explore AND document):
The user says "let me explore [X] properly", "capture these findings",
"record this as an exploration area", "think through [X] and document it"
— phrases that combine exploration with documentation intent.
- Move through steps 1-2 faster (the user wants structured output).
- At step 3, the user has already signaled capture intent, so move to step 4.
- **Crucially: still do step 4 (Present & Confirm).** Present what you'd write
  and ask "Does this look right?" before creating files.
- Never skip step 4 — the user confirming the *topic* doesn't mean they've
  confirmed the *content*.

If unsure, default to Explore Mode.

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

After creating the bootstrap files, proceed with the workflow below.

## Workflow: Following the Loop

This replaces the old separate Capture/Explore workflows. Every session follows
The Exploration Loop above. The only variable is *pace*.

### Step 1: Read Context

Before anything else, read these to understand what already exists:
1. `exploration/_index.md` — dashboard, cross-cutting decisions, session log
2. `exploration/_template/README.md` — template structure

If either file is missing, run the bootstrap setup first.

### Step 2: Check for Overlaps

Read existing area READMEs that might relate to the topic. If an area already
covers similar ground, offer to update it instead of creating a new one.
List the overlap clearly so the user can decide.

### Step 3-4: Discuss, Explore, Iterate (The Loop)

This is the core. Follow The Exploration Loop:

1. **Listen & Map** — Understand the topic, ground in codebase context
2. **Discuss & Explore** — Use diagrams, comparisons, open questions
3. **Pause & Ask Direction** — "Is there more? Or shall I capture this?"
   - If "keep exploring" → loop back to step 2
   - If "capture it" → move to step 4
4. **Present & Confirm** — "Here's what I'd write. Does this look right?"
   - Show the summary, scope, key findings you'd capture
   - Wait for the user to agree before creating files
5. **Write to Files** — Only now create or update files
6. **"What next?"** — After writing, ask the user what to explore next

**Key rule**: Never skip step 4 (Present & Confirm). The user must see and
approve what you plan to write before you write it.

### Step 5: Capture into Structure

Only proceed here after the user has confirmed the content at step 4.

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

### Step 5b: Link Coherence Check

After writing the area files, verify structural link integrity before updating
the dashboard. This catches missing backlinks, dangling references, and orphans
before they accumulate.

1. Run the coherence checker from the project root:
   ```bash
   python scripts/check_link_coherence.py
   ```
2. Present each issue to the user along with a suggested resolution:
   - **Bidirectional miss**: "Area B's Depends on doesn't mention this area.
     Should we add it?"
   - **Dangling link**: "This area links to 'ghost-area/' which doesn't exist.
     Remove the link or create the area?"
   - **Status mismatch**: "This area depends on 'legacy-module' which is
     'dropped'. Reconsider your dependency?"
   - **Orphan area**: "Area 'api-design' exists on disk but isn't in the
     dashboard. Add it?"
3. Apply the agreed resolution (edit the relevant area's Links section or
   `_index.md`).
4. Re-run the checker to confirm all issues are resolved before moving on.

The script is purely diagnostic — it never auto-fixes. You decide what to do
with each finding.

### Step 6: Update _index.md

1. Add a row to the **Status Dashboard** (for new areas)
2. Add a row to the **Session Log** (for this session)
3. If a cross-cutting decision emerged, add it to **Cross-Cutting Decisions**

Always update `_index.md` before finishing — a new area without a dashboard entry
is invisible. A session without a log entry is lost.

### Step 6b: Semantic Coherence Check

After the dashboard is updated, review linked areas for conceptual consistency.
This catches contradictions and stale assumptions that structural checks miss.

1. Read the README.md of every area listed in Depends on and Feeds into
2. Read relevant Cross-Cutting Decisions from `_index.md`
3. Compare against what was just written. Surface any:
   - **Contradictions**: findings in the new area that conflict with findings
     in a linked area. Explain the conflict so the user can decide which to
     revise.
   - **Stale decisions**: a cross-cutting decision that the new findings
     invalidate or make obsolete.
   - **Answered questions**: linked areas' Open Questions that your findings
     resolve. Flag them so the user can close them out.
   - **Status signals**: areas whose status may need updating (e.g., a linked
     area's findings are superseded, or a dependency just became `saturated`).
4. Present these as observations, not commands. The user decides what to do.
5. Apply any agreed-upon changes (update findings, close questions, adjust
   statuses, revise decisions).

This step keeps the exploration coherent as it grows. Without it, two areas
can silently contradict each other.

### Step 7: Loop Back

After writing, always ask: "What should we explore next?" This returns to
step 1 of the loop for a new topic or step 2 for the same topic.

## Maintaining an Existing Area

When the user asks to explore within an existing area, or findings update one:

1. Read the area's README.md and notes.md
2. Explore the new angle (steps 2-3 of the loop)
3. Present & Confirm: "I'd add [finding X] and refine [question Y] — agree?"
4. If the user agrees, edit the README and update `last-updated` in frontmatter
5. Run the coherence check (Step 5b) and semantic check (Step 6b) — the
   update may have created inconsistencies with linked areas
6. Ask: "What next?"

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

- **No write without confirmation** — Never create, edit, or delete files
  without the user explicitly agreeing to the content first. Step 4 (Present &
  Confirm) is mandatory in every session.
- **Don't implement** — Never write application code. Creating exploration files
  is capturing thinking, not implementing. If the user asks to implement, suggest
  finishing exploration and using a change proposal workflow instead.
- **Don't force structure before exploration** — Let the user explore freely.
  Premature structure shuts down thinking.
- **Do capture when the user is ready** — When the user says "capture it" or
  "write it up", stop exploring and move to Present & Confirm.
- **Do read related areas first** — New areas should always link to existing ones.
  Stale or missing links are worse than no links.
- **Do keep READMEs polished** — notes.md can be messy, but README.md is the
  public face of an area.
- **Do update _index.md** — A new area without a dashboard entry is invisible.
- **Do loop back** — After writing, always ask "what next?" to keep the
  exploration going.
- **Do check link coherence** — After writing, always run the coherence checker
  and resolve structural issues. A stale link graph undermines the value of the
  exploration.
- **Do check semantic coherence** — After updating the dashboard, always read
  linked areas and surface contradictions. Silent inconsistencies compound over
  time.
- **Don't create changes** — That's the next step, not this skill's job.
