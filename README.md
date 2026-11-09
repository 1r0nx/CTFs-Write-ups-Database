# CTFs Write-ups Database

A searchable collection of solved CTF challenge write-ups.

## What's inside

- 279 solved challenges across several CTFs (Pwny-CTF, 2026-battleCTF, 2026-hiCTF, 2026-PINK, Root-Me, 2025_SADC-NextGenCyber-CTF, 2026-EHAX-CTF).
- Each challenge has its own `writeup.md` with a fixed, machine-parseable structure: YAML frontmatter (`title`, `ctf`, `category`, `difficulty`, `points`, `techniques`, `tools`, `keywords`, `status`, `has_script`, `source`) followed by sections `Summary`, `Statement and artefacts`, `Recognition signals`, `Resolution method`, `Discarded approaches` (optional), `Solve script` (optional), `Flag`, `Lessons and reusable patterns`.
- No cross-references: every write-up stands on its own.
- All flags are preserved exactly.
- Provided challenge files are not copied; only `writeup.md` is shipped.

## Searching the database: `ctf-find`

`ctf-find` is a small full-text search tool (SQLite FTS5, no AI) over the write-ups. It indexes the frontmatter fields (CTF, category, techniques, keywords, tools) and the full body of every `writeup.md`.

```bash
./ctf-find heap overflow
./ctf-find -c crypto rsa
./ctf-find -C hiCTF lattice
./ctf-find -n 20 format string
```

Options:

- `-c, --cat` filter by category (e.g. `crypto`, `pwn`, `web`, `forensics`, `reverse`, `misc`, `stego`)
- `-C, --ctf` filter by CTF name (e.g. `Pwny-CTF`, `hiCTF`)
- `-n` number of results (default 8)
- `CTF_DB` env var to point at a different root directory

Results show the CTF, category, challenge, techniques, a snippet, and the path to the write-up.

## Repository layout

```
<CTF>/<CHALLENGES>/<Category>/<Challenge>/writeup.md
```

## Controlled vocabulary

See `TAXONOMY.md` for the controlled lists of categories, techniques, tools and keywords. `INDEX.md` lists every challenge.
