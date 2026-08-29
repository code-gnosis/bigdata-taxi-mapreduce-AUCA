#!/usr/bin/env python3
"""
(a) HOURLY TAXI DEMAND -- mapper.

KEY   = hour of day (00..23), zero-padded so the Shuffle-and-Sort lexical ordering
        also happens to be chronological ("09" < "10"). Without padding you would get
        0,1,10,11,...,2,20 -- a classic streaming-sort trap.
VALUE = "1,fare,total" -- a partial aggregate, not a bare 1. Carrying the sums here lets
        the SAME reducer be reused as a combiner without changing a line of code.
"""
import sys

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        hour, fare, total = f[11], float(f[7]), float(f[10])
    except ValueError:
        continue
    print(f"{int(hour):02d}\t1,{fare:.2f},{total:.2f}")
