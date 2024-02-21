import time
import sys

from ays_agent.stat.cpu import CPUMonitor
from ays_agent.stat.disk import DiskMonitor
from ays_agent.stat.memory import MemoryMonitor
from ays_agent.stat.network import NetworkMonitor

cpu = CPUMonitor()
cpu.start()
disk = DiskMonitor("/")
disk.start()
mem = MemoryMonitor()
mem.start()
net = NetworkMonitor()
net.start()
while True:
    time.sleep(1)
    sent, recv, up, dl = net.get_formatted_stats(1)
    cpu_cores, cpu_usage = cpu.get_formatted_stats()
    mem_total, mem_used, mem_percent = mem.get_formatted_stats()
    disk_total, disk_used, disk_percent, disk_reads, disk_writes, disk_r, disk_w = disk.get_formatted_stats(1)
    print(f"Network Up: {sent} DL: {recv} Up Speed: {up}/s DL Speed: {dl}/s"
          f", CPU {cpu_cores} {cpu_usage}    ",
          f", Memory {mem_used} of {mem_total} {mem_percent}   ",
          f", Disks {disk_used} of {disk_total} {disk_percent}, R {disk_reads} W {disk_writes}, R {disk_r}/s W {disk_w}/s    ",
          end="\r")
