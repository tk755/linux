# Niri JSON IPC shared by the workspace and Bitwarden scripts
# https://github.com/niri-wm/niri/blob/v26.04/niri-ipc/src/lib.rs

import json
import os
import socket
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, TextIO


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
