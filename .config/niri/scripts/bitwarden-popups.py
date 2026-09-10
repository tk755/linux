#!/usr/bin/env python3
# float Bitwarden popups after Firefox sets their extension title
# adapted from: https://github.com/niri-wm/niri/discussions/1599

import json
import os
import socket
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, TextIO

WIDTH = 450
HEIGHT = 600
GAP = 8


@contextmanager
def connect() -> Iterator[socket.socket]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(5)
        connection.connect(os.environ["NIRI_SOCKET"])
        yield connection


def send(connection: socket.socket, message: str | dict[str, Any]) -> None:
    connection.sendall((json.dumps(message) + "\n").encode())


def reply(stream: TextIO) -> Any:
    line = stream.readline()
    if not line:
        raise ConnectionError("Niri closed the IPC connection")
    result = json.loads(line)
    if "Err" in result:
        raise RuntimeError(result["Err"])
    return result["Ok"]


def request(message: str | dict[str, Any]) -> Any:
    with connect() as connection, connection.makefile("r", encoding="utf-8") as stream:
        send(connection, message)
        return reply(stream)


def configure_popup(window: dict[str, Any]) -> None:
    workspaces = request("Workspaces")["Workspaces"]
    workspace = next((w for w in workspaces if w["id"] == window["workspace_id"]), None)
    if workspace is None:
        raise RuntimeError("workspace no longer exists")
    output = workspace["output"]
    screen = request("Outputs")["Outputs"][output]["logical"]
    layout = window["layout"]
    border = layout["tile_size"][0] - layout["window_size"][0]
    # positions are relative to the working area, below Waybar
    x, y = max(GAP, screen["width"] - WIDTH - border - GAP), GAP

    window_id = window["id"]
    for name, options in (
        ("MoveWindowToFloating", {}),
        ("SetWindowWidth", {"change": {"SetFixed": WIDTH}}),
        ("SetWindowHeight", {"change": {"SetFixed": HEIGHT}}),
        ("MoveFloatingWindow", {"x": {"SetFixed": x}, "y": {"SetFixed": y}}),
    ):
        request({"Action": {name: {"id": window_id, **options}}})


def watch(stream: TextIO) -> None:
    handled = set()
    for line in stream:
        event = json.loads(line)
        if closed := event.get("WindowClosed"):
            handled.discard(closed["id"])
            continue
        if changed := event.get("WindowsChanged"):
            windows = changed["windows"]
            handled.intersection_update(window["id"] for window in windows)
        elif changed := event.get("WindowOpenedOrChanged"):
            windows = [changed["window"]]
        else:
            continue

        for window in windows:
            if window["id"] in handled or window["app_id"] != "firefox":
                continue
            if not (window["title"] or "").startswith("Extension: (Bitwarden Password Manager)"):
                continue
            # run once per popup; leave later manual moves and resizes alone
            handled.add(window["id"])
            try:
                configure_popup(window)
            except (OSError, RuntimeError, KeyError, ValueError) as error:
                print(f"bitwarden popup {window['id']}: {error}", file=sys.stderr)


def main() -> int:
    try:
        with connect() as connection, connection.makefile("r", encoding="utf-8") as stream:
            send(connection, "EventStream")
            reply(stream)
            # only the established event stream waits indefinitely
            connection.settimeout(None)
            watch(stream)
    except (OSError, RuntimeError, KeyError, ValueError) as error:
        print(f"bitwarden popups: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
