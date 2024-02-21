import psutil

class CPUMonitor(object):
    def __init__(self):
        self.cores = psutil.cpu_count(logical=False)

    def start(self):
        # Provides a meaningless value, 0.0, which should be ignored (per docs)
        psutil.cpu_percent(interval=None)

    def get_stats(self) -> tuple[int, int]:
        """ Get CPU stats.

        @returns number of logical CPU cores and percent utilization
        """
        usage = psutil.cpu_percent(interval=None)
        return self.cores, usage

    def get_formatted_stats(self) -> tuple[int, int]:
        cores, usage = self.get_stats()
        return cores, f"{usage}%"

