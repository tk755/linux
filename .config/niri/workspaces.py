#!/usr/bin/env python3
"""Name workspaces with fuzzel; release empty names after leaving the workspace.

Uses niri's JSON IPC and stable workspace IDs, including across monitor moves.
https://github.com/niri-wm/niri/blob/v26.04/niri-ipc/src/lib.rs
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


def connect():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect(os.environ["NIRI_SOCKET"])
    except BaseException:
        sock.close()
        raise
    return sock


def send(sock, message):
    sock.sendall((json.dumps(message) + "\n").encode())


def reply(stream):
    line = stream.readline()
    if not line:
        raise ConnectionError("niri closed the IPC connection")
    result = json.loads(line)
    if "Err" in result:
        raise RuntimeError(result["Err"])
    return result["Ok"]


def request(message):
    with connect() as sock, sock.makefile("r", encoding="utf-8") as stream:
        send(sock, message)
        return reply(stream)


def workspaces():
    return request("Workspaces")["Workspaces"]


def name_workspace():
    workspace = next((w for w in workspaces() if w["is_focused"]), None)
    if workspace is None:
        return
    result = subprocess.run(
        ["fuzzel", "--dmenu", "--prompt-only=Workspace name: ",
         "--search=" + (workspace["name"] or "")],
        input="", capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return  # Escape cancels without changing the existing name.
    name = result.stdout.strip()
    if not name:
        return  # Empty input is also a cancellation; cleanup handles empty workspaces.
    current = workspaces()
    if not any(w["id"] == workspace["id"] for w in current):
        raise RuntimeError("the workspace was removed while the prompt was open")
    if any(w["name"] == name and w["id"] != workspace["id"] for w in current):
        raise RuntimeError("that workspace name is already in use")
    request({"Action": {"SetWorkspaceName": {
        "name": name, "workspace": {"Id": workspace["id"]},
    }}})


def can_clean(workspace, occupied):
    return (
        workspace["name"] is not None
        and workspace["output"] is not None
        and not workspace["is_active"]
        and workspace["active_window_id"] is None
        and workspace["id"] not in occupied
    )


def clean_empty_names():
    # Query fresh state instead of acting on possibly queued events. Count floating
    # windows too; another monitor's visible workspace must retain its name.
    occupied = {w["workspace_id"] for w in request("Windows")["Windows"]}
    for candidate in workspaces():
        if not can_clean(candidate, occupied):
            continue
        # Reordering and closing windows can remove/reindex other workspaces.
        # Recheck by stable ID immediately before removing the name.
        current = next((w for w in workspaces() if w["id"] == candidate["id"]), None)
        if current and current["name"] == candidate["name"] and can_clean(current, occupied):
            request({"Action": {"UnsetWorkspaceName": {
                "reference": {"Id": current["id"]},
            }}})


def watch_once():
    with connect() as sock, sock.makefile("r", encoding="utf-8") as stream:
        send(sock, "EventStream")
        reply(stream)
        sock.settimeout(None)
        for line in stream:
            event = json.loads(line)
            if any(kind in event for kind in (
                "WorkspacesChanged", "WorkspaceActivated", "WorkspaceActiveWindowChanged",
                "WindowsChanged", "WindowOpenedOrChanged", "WindowClosed",
            )):
                clean_empty_names()


def watch():
    # A temporary IPC failure should not silently disable cleanup for the session.
    while Path(os.environ["NIRI_SOCKET"]).exists():
        try:
            watch_once()
        except (OSError, RuntimeError, ValueError) as error:
            print(f"workspace cleanup: {error}", file=sys.stderr, flush=True)
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("name", "watch"))
    args = parser.parse_args()
    try:
        if args.command == "name":
            name_workspace()
        else:
            watch()
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print(f"niri workspaces: {error}", file=sys.stderr)
        if args.command == "name":
            subprocess.run(["notify-send", "Workspace name", str(error)], check=False)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
