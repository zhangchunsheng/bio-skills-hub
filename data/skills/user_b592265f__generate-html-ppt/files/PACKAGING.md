# Lightweight Codex skill package

The repository retains `demo/` so GitHub readers can browse the complete
gallery and README animations. It is intentionally excluded from the Codex
installation archive: the skill can select and build every template from the
text metadata and individual `design.md` files alone.

Build the installable core archive from the repository root:

```bash
bash scripts/package-core-skill.sh
```

The resulting `dist/generate-html-ppt-core.tar.gz` contains only runtime
instructions, HTML templates, references, and scripts. It excludes `demo/`,
binary screenshot backgrounds, Git metadata, editor files, and Python bytecode.
This keeps it compatible with registries that accept text-based skill packages
only. To replace an old archive, delete it first, then run the command again.

For a visual style comparison, the agent should create a small, topic-specific
HTML preview when needed. The source gallery remains available in this
repository but is not a dependency of the core skill.
