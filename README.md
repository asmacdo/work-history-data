# work-history-data

GitHub activity of `asmacdo` (issues and PRs opened or assigned, as per-day lists of URLs), collected by [historia](https://github.com/CodyCBakerPhD/historia).
Feeds the [Austin's Work](https://github.com/orgs/con/projects/14) board in the `con` org, a copy of the team's "Work template".

## Automation

Two scheduled workflows, both modeled on [CodyCBakerPhD/work-history-data](https://github.com/CodyCBakerPhD/work-history-data):

- `update.yml` (daily, or `workflow_dispatch` with a `recency` input): fetch recent activity, commit it, add new items to the board's `Incoming` column, refresh dates, and push a compressed archive to the `dist` branch.
- `move-done-to-history.yml` (daily): sweep the board's `DONE` column into `History`.

They need one repository secret, `GH_PAT`: a fine-grained token with resource owner `con`, repository access "Public repositories", and organization permission `Projects: read and write`.
It only reads activity and writes the board; pushes use the workflow's own `GITHUB_TOKEN`.

## Layout

- `history/` — historia JSON snapshots. Ephemeral: fully regenerable from GitHub by re-running `historia update github` with a wider `--recency`.
- `scripts/migrate-to-con.py` — the one-time card migration from the previous user-owned board (`asmacdo/projects/7`) to the `con` board, kept for the record.
- `.venv-host/` — local Python venv (gitignored) for running historia by hand.

## Running historia by hand

```
uv venv .venv-host && uv pip install --python .venv-host/bin/python historia
export GITHUB_TOKEN="$(gh auth token)"
.venv-host/bin/historia update github --directory ./history --username asmacdo --recency 3
.venv-host/bin/historia project populate --directory ./history --url https://github.com/orgs/con/projects/14 --status Incoming --yes
```

## STAMPED properties

- **Self-contained / Actionable:** this README plus the workflows are sufficient to recreate.
- **Tracked:** plain git; the action commits each run.
- **Ephemeral:** `history/` is a cache; GitHub is the source.
- **Portable:** no hardcoded paths in tracked files.
- **Distributable:** swap `USERNAME` and `PROJECT_URL` in `update.yml` and a fork serves anyone else.
