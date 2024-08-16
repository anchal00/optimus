import subprocess
from threading import Thread

import time
import re


def call(domain):
    st = time.perf_counter()
    s = subprocess.Popen(
        f"dig +retry=0 +timeout=30 @localhost -p 8000 {domain}".split(" "),
        stdout=subprocess.PIPE,
    )
    stdout, _ = s.communicate()
    total = time.perf_counter() - st
    STATUS_REGEX = r"status: \w+,"
    s: str = stdout.decode("utf-8")
    match: re.Match = re.findall(STATUS_REGEX, s)
    print(f"Process {domain} took {total}ms { match[0]}")
    return True


domains = [
    "meet.new",
    "sheets.new",
    "roadmap.sh",
    "google.com",
    "youtube.com",
    "yahoo.com",
    "netflix.com",
    "github.com",
]

ps = []

for i in range(60):
    p = Thread(target=call, args=(domains[i % len(domains)],))
    p.start()
    ps.append(p)

for p in ps:
    p.join()
