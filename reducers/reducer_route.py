#!/usr/bin/env python3
"""
(g) BUSIEST ROUTES -- reducer.
OUTPUT: route \t trips, revenue, avg_revenue
Top-20 ranking is deliberately left to a later stage / post-processing, for the same reason
as the location job: ranking is global and a reducer only sees its own key group.
"""
import sys

def flush(k, n, rev):
    if k is None:
        return
    print(f"{k}\t{n}\t{rev:.2f}\t{rev/n if n else 0:.2f}")

cur, n, rev = None, 0, 0.0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    try:
        c, total = val.split(",")
        c = int(c); total = float(total)
    except ValueError:
        continue
    if key != cur:
        flush(cur, n, rev)
        cur, n, rev = key, 0, 0.0
    n += c; rev += total
flush(cur, n, rev)
