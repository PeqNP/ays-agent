import psutil

from ays_agent.stat import format_bytes, get_base

class NetworkMonitor(object):
    def __init__(self):
        self.bytes_sent = 0
        self.bytes_recv = 0

    def start(self):
        """ Start monitoring network traffic. """
        io = psutil.net_io_counters()
        self.bytes_sent, self.bytes_recv = io.bytes_sent, io.bytes_recv

    def get_stats(self, delay: int) -> tuple[int, int, int, int]:
        """ Get network stats since last delay.

        @returns the number of bytes sent, bytes received, upload speed, and
        download speed.
        """
        io = psutil.net_io_counters()
        up_speed, dl_speed = (io.bytes_sent - self.bytes_sent) / delay, (io.bytes_recv - self.bytes_recv) / delay
        self.bytes_sent, self.bytes_recv = io.bytes_sent, io.bytes_recv
        return self.bytes_sent, self.bytes_recv, up_speed, dl_speed

    def get_formatted_stats(self, delay: int) -> tuple[str, str, str, str]:
        """ Get formatted network stats since last delay. """
        base = get_base()
        stats = self.get_stats(delay)
        stats = tuple(map(lambda x: format_bytes(x, base), stats))
        return stats
