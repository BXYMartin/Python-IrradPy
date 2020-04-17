import os
import sys
import tempfile
import argparse
import datetime
import multiprocessing
from typing import List
from typing import Optional
from typing import Union
from pathlib import Path
from .process import SocketManager

def run(
    data_dir: Optional[Union[str, Path]] = os.path.join(os.getcwd(), "PNNL_data"),
    merge_timelapse: str = 'monthly',
    ):

    socket = SocketManager()
    socket.convert(data_dir, merge_timelapse)
