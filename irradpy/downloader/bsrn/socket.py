#!/usr/bin/env python
# encoding: utf-8

from typing import Optional
from typing import Union
from pathlib import Path
from .process import SocketManager


def run(
        download_directory: Optional[Union[str, Path]] = None
    ):
    socket = SocketManager()
    socket.run(download_directory)
