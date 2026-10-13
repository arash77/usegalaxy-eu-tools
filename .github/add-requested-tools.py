#!/usr/bin/env python3
"""Add the tools of a Galaxy tool installation request to this repository.

tool-installation-requests.sh runs this as APPLY_COMMAND, with the work item
from ``consume-tool-installation-requests emit`` in the file named by $ITEM.
A tool that a tool list here has already gets the requested revisions in that
list's lock file. Other tools are added to diverse.yaml and its lock file.
"""

import glob
import json
import os

import yaml

NEW_TOOLS = "diverse.yaml"


def same_repository(a, b):
    return a["name"] == b["name"] and a["owner"] == b["owner"]


def tool_list_of(tool):
    for path in sorted(glob.glob("*.yaml")):
        with open(path) as f:
            if any(same_repository(t, tool) for t in (yaml.safe_load(f) or {}).get("tools", [])):
                return path
    return None


def main():
    with open(os.environ["ITEM"]) as f:
        item = json.load(f)
    for tool in item["tools"]:
        tool_list = tool_list_of(tool)
        if tool_list is None:
            tool_list = NEW_TOOLS
            # Append as text, so that the hand-written tool list keeps its comments.
            with open(tool_list, "a") as f:
                f.write(
                    f"\n  - name: {tool['name']}\n    owner: {tool['owner']}\n"
                    f"    tool_panel_section_label: {tool['tool_panel_section_label']}\n"
                )
        with open(f"{tool_list}.lock") as f:
            lock = yaml.safe_load(f)
        entry = next((t for t in lock["tools"] if same_repository(t, tool)), None)
        if entry is None:
            entry = {"name": tool["name"], "owner": tool["owner"], "revisions": []}
            entry["tool_panel_section_label"] = tool["tool_panel_section_label"]
            lock["tools"].append(entry)
        revisions = set(entry.get("revisions") or [])
        if set(tool.get("revisions", [])) <= revisions:
            continue
        entry["revisions"] = sorted(revisions | set(tool["revisions"]))
        # Write the lock file the way scripts/fix-lockfile.py does.
        with open(f"{tool_list}.lock", "w") as f:
            yaml.dump(lock, f, default_flow_style=False)


if __name__ == "__main__":
    main()
