#!/usr/bin/env python3
"""One-time migration of the Work History board from asmacdo/projects/7 to con/projects/14.

Copies every card (issues, PRs, and draft cards) and maps its column onto the con
template's columns. Dry-run by default: prints what it would do. Pass --apply to write.
Idempotent: cards already on the target are only touched if their Status differs, so a
partial run can simply be re-run.

Dates are not copied: `historia project update dates --url <target>` (no --recency)
backfills Start/End date for every item from GitHub after this runs.

Needs `gh` authenticated with project scope on both the user and the con org.
"""

import argparse
import json
import subprocess
import sys

SOURCE = {"number": 7, "owner": "asmacdo"}
TARGET = {"number": 14, "owner": "con"}

# old column -> template column (decisions 2026-09-10; UNTRACKED existed only because
# nothing swept the old Done, and the con board sweeps DONE -> History daily)
COLUMN_MAP = {
    "Incoming": "Incoming",
    "Backlog": "BACKLOG",
    "On Radar": "ON RADAR",
    "Todo": "TODO",
    "Agenda": "Agenda",
    "Done": "History",
    "UNTRACKED": "DONE",
}


def gh(*args):
    """Run a gh command, return parsed JSON (all calls here use --format json)."""
    result = subprocess.run(["gh", *args, "--format", "json"], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args)} failed:\n{result.stderr}")
    return json.loads(result.stdout)


def list_items(project):
    return gh("project", "item-list", str(project["number"]), "--owner", project["owner"], "--limit", "2000")["items"]


def target_status_field():
    """Return (project_id, status_field_id, {option name: option id}) for the target board."""
    fields = gh("project", "field-list", str(TARGET["number"]), "--owner", TARGET["owner"])["fields"]
    status = next(f for f in fields if f["name"] == "Status")
    project_id = gh("project", "view", str(TARGET["number"]), "--owner", TARGET["owner"])["id"]
    return project_id, status["id"], {o["name"]: o["id"] for o in status["options"]}


def set_status(project_id, item_id, field_id, option_id):
    gh("project", "item-edit", "--project-id", project_id, "--id", item_id,
       "--field-id", field_id, "--single-select-option-id", option_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="write to the target board (default: dry run)")
    args = parser.parse_args()

    project_id, status_field_id, options = target_status_field()
    missing = set(COLUMN_MAP.values()) - set(options)
    if missing:
        sys.exit(f"target board lacks columns {sorted(missing)}; has {sorted(options)}")

    source_items = list_items(SOURCE)
    # Existing target cards keyed by content URL (issues/PRs) or by title (drafts have no URL).
    existing = {}
    for item in list_items(TARGET):
        key = item["content"].get("url") or ("draft", item["title"])
        existing[key] = item

    counts = {"add": 0, "create-draft": 0, "restatus": 0, "unchanged": 0, "skip": 0}
    for item in source_items:
        content = item["content"]
        old_col = item.get("status")
        new_col = COLUMN_MAP.get(old_col)
        if new_col is None:
            print(f"SKIP   unmapped column {old_col!r}: {item['title']}")
            counts["skip"] += 1
            continue

        is_draft = content["type"] == "DraftIssue"
        key = ("draft", item["title"]) if is_draft else content["url"]
        label = item["title"] if is_draft else content["url"]
        target = existing.get(key)

        if target is None:
            action = "create-draft" if is_draft else "add"
        elif target.get("status") != new_col:
            action = "restatus"
        else:
            action = "unchanged"
        counts[action] += 1
        print(f"{action:<12} {old_col:<9} -> {new_col:<8} {label}")

        if not args.apply or action == "unchanged":
            continue
        if action == "add":
            target = gh("project", "item-add", str(TARGET["number"]), "--owner", TARGET["owner"], "--url", content["url"])
        elif action == "create-draft":
            target = gh("project", "item-create", str(TARGET["number"]), "--owner", TARGET["owner"],
                        "--title", item["title"], "--body", content.get("body") or "")
        set_status(project_id, target["id"], status_field_id, options[new_col])

    print(f"\n{'applied' if args.apply else 'dry run'}: {counts} ({len(source_items)} source cards)")


if __name__ == "__main__":
    main()
