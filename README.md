# work-history-data

Personal backup of GitHub activity for `asmacdo`, populated by [historia](https://github.com/CodyCBakerPhD/historia).
Feeds a personal GitHub Projects v2 board used as a cross-repo dashboard.

## Status

Solo / no upstream / no cron — all updates manual.
Design context and integration goals live in [asmacdo/notes projects/historia/CONTEXT.md](https://github.com/asmacdo/notes/blob/main/projects/historia/CONTEXT.md).

## Reproduce

```
python3 -m venv .venv-host && source .venv-host/bin/activate
pip install historia
export GITHUB_TOKEN="$(gh auth token)"
historia update github --directory ./history --username asmacdo --recency 3
```

To populate a project board:

```
historia project populate --directory ./history --url <project-url>
```

## Layout

- `history/` — historia JSON snapshots.
  **Ephemeral** — fully regenerable from GitHub by re-running `historia update github` with a wider `--recency`.
- `.venv-host/` — Python venv (gitignored).

## STAMPED properties

- **Self-contained / Actionable:** this README is sufficient to recreate.
- **Tracked:** plain git.
- **Ephemeral:** `history/` is a cache; GitHub is the source.
- **Modular:** venv and data are separate concerns.
- **Portable:** no hardcoded paths in tracked files.
- **Distributable:** swap `--username` and a clone serves anyone else.
