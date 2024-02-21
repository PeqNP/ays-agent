import psutil

from ays_agent.stat import format_bytes

class MemoryMonitor(object):
    def __init__(self):
        self.cores = psutil.cpu_count(logical=False)

    def start(self):
        pass

    def get_stats(self) -> tuple[int, int, int]:
        """ Get memory stats.

        @returns total, used, and percent of memory used
        """
        mem = psutil.virtual_memory()
        return mem.total, mem.total - mem.available, mem.percent

    def get_formatted_stats(self) -> tuple[str, str, str]:
        total, used, percent = self.get_stats()
        return format_bytes(total), format_bytes(used), f"{percent}%"

