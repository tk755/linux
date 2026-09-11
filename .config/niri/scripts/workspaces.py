#!/usr/bin/env python3
# name workspaces through Fuzzel; release names when empty and inactive

import argparse
import json
import os
import subprocess
import sys
from typing import Any, TextIO

from niri_ipc import connect, reply, request, send


def workspaces() -> list[dict[str, Any]]:
    return request("Workspaces")["Workspaces"]


def rename_workspace() -> None:
    workspace = next((w for w in workspaces() if w["is_focused"]), None)
    if workspace is None:
        return
    result = subprocess.run(
        [
            "fuzzel",
            "--dmenu",
            "--prompt-only=Workspace: ",
            "--override=key-bindings.execute=none",
            "--override=key-bindings.execute-input="
            "Return KP_Enter Control+y Shift+Return Shift+KP_Enter",
            "--search=" + (workspace["name"] or ""),
            "--output=" + workspace["output"],
            "--anchor=top",
            "--y-margin=8",
            "--width=30",
            "--layer=overlay",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return
    name = result.stdout.strip()
    if name == (workspace["name"] or ""):
        return
    current = workspaces()
    if not any(w["id"] == workspace["id"] for w in current):
        raise RuntimeError("workspace no longer exists")
    if not name:
        request({"Action": {"UnsetWorkspaceName": {"reference": {"Id": workspace["id"]}}}})
        return
    if any(w["name"] == name and w["id"] != workspace["id"] for w in current):
        raise RuntimeError("workspace name is already in use")
    # retain the original target even if focus or workspace indices changed during input
    request({"Action": {"SetWorkspaceName": {"name": name, "workspace": {"Id": workspace["id"]}}}})


def can_clean(workspace: dict[str, Any]) -> bool:
    return (
        workspace["name"] is not None
        and workspace["output"] is not None
        and not workspace["is_active"]
        and workspace["active_window_id"] is None
    )


def clean_empty_names() -> None:
    for candidate in workspaces():
        if not can_clean(candidate):
            continue
        # count floating windows too; active_window_id alone is not an occupancy check
        occupied = {w["workspace_id"] for w in request("Windows")["Windows"]}
        if candidate["id"] in occupied:
            continue
        # confirm the name and visibility before releasing a potentially stale candidate
        current = next((w for w in workspaces() if w["id"] == candidate["id"]), None)
        if current and current["name"] == candidate["name"] and can_clean(current):
            request({"Action": {"UnsetWorkspaceName": {"reference": {"Id": current["id"]}}}})


def watch(stream: TextIO) -> None:
    for line in stream:
        event = json.loads(line)
        if any(
            kind in event
            for kind in (
                "WorkspacesChanged",
                "WorkspaceActivated",
                "WorkspaceActiveWindowChanged",
                "WindowsChanged",
                "WindowOpenedOrChanged",
                "WindowClosed",
            )
        ):
            clean_empty_names()


def label(stream: TextIO) -> None:
    output = os.environ.get("WAYBAR_OUTPUT_NAME")
    for line in stream:
        event = json.loads(line)
        if not any(
            kind in event
            for kind in ("WorkspacesChanged", "WorkspaceActivated", "WorkspaceUrgencyChanged")
        ):
            continue
        current = workspaces()
        if output:
            workspace = next((w for w in current if w["output"] == output and w["is_active"]), None)
        else:
            workspace = next((w for w in current if w["is_focused"]), None)
        label = {"text": "", "class": ""}
        if workspace:
            label["text"] = workspace["name"] or str(workspace["idx"])
            label["class"] = "urgent" if workspace["is_urgent"] else ""
        print(json.dumps(label), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Name workspaces and clean up empty names")
    parser.add_argument("command", choices=("rename", "watch", "label"))
    args = parser.parse_args()
    try:
        if args.command == "rename":
            rename_workspace()
        else:
            with connect() as connection, connection.makefile("r", encoding="utf-8") as stream:
                send(connection, "EventStream")
                reply(stream)
                connection.settimeout(None)
                if args.command == "label":
                    label(stream)
                else:
                    watch(stream)
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print(f"niri workspaces: {error}", file=sys.stderr)
        if args.command == "rename":
            subprocess.run(["notify-send", "Workspace name", str(error)], check=False)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
