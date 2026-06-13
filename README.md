# Skills Collection

Agent skills for [opencode](https://opencode.ai). Install skills from this repository with the Skills CLI.

## Available Skills

### [structured-explore](structured-explore/SKILL.md)

Explore complex problems and capture findings into structured `exploration/` directories. Creates per-area READMEs with YAML frontmatter, findings, open questions, and cross-links — feeds directly into specification writing.

**Install:**
```bash
npx skills add jorge-romero/skills-collection@structured-explore -g
```

**Usage:** Tell your agent to "explore X properly" or "capture these findings" — it will create the directory structure, write findings, and update the dashboard.

---

## Development

To add a new skill, create a directory with a `SKILL.md` at minimum. Optional `scripts/`, `references/`, and `assets/` directories can bundle resources.

```bash
npx skills add jorge-romero/skills-collection@your-skill-name
```

## License

MIT
