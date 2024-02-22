import logging
import psutil
import sys

from typing import List
from typing_extensions import Optional

from ays_agent.stat import format_bytes, get_base, get_megabytes, get_default_mountpoint

class DiskMonitor(object):
    def __init__(self, path: Optional[str] = None):
        # Disk path (mountpoint) to monitor
        self.path = path or get_default_mountpoint()
        self.bytes_read = 0
        self.bytes_written = 0

    def start(self):
        """ Start monitoring network traffic. """
        io = psutil.disk_io_counters()
        self.bytes_read, self.bytes_written = io.read_bytes, io.write_bytes

    def get_num_disk(self):
        """ Get the number of physical devices. Ignores pseudo, memory, duplicate, etc. """
        disks = psutil.disk_partitions(all=False)
        return len(disks)

    def get_stats(self, delay: int) -> tuple[int, int, int, int, int, int]:
        """ Get disk stats from last delay.

        @returns total, used, percent, total bytes read, total bytes written, bytes read, bytes written
        """
        usage = psutil.disk_usage(self.path)
        io = psutil.disk_io_counters()
        num_read, num_written = (io.read_bytes - self.bytes_read) / delay, (io.write_bytes - self.bytes_written) / delay
        self.bytes_read, self.bytes_written = io.read_bytes, io.write_bytes
        return usage.total, usage.used, usage.percent, self.bytes_read, self.bytes_written, num_read, num_written

    def get_formatted_stats(self, delay: int) -> tuple[str, str, str, str]:
        """ Get formatted network stats since last delay. """
        total, used, percent, bytes_read, bytes_written, bytes_r, bytes_w = self.get_stats(delay)
        base = get_base()
        def fb(bytes: int) -> str:
            return format_bytes(bytes, base)
        return fb(total), fb(used), f"{percent}%", fb(bytes_read), fb(bytes_written), fb(bytes_r), fb(bytes_w)

    def get_values(self, delay: int) -> List[dict]:
        """ Get list of values that represent an `AgentValue`. """
        total, used, percent, bytes_read, bytes_written, bytes_r, bytes_w = self.get_stats(delay)
        return [
            {"name": "Disk Used %", "value": percent},
            {"name": "Disk R/s", "value": get_megabytes(bytes_r)},
            {"name": "Disk W/s", "value": get_megabytes(bytes_w)}
        ]
