#!/usr/bin/env python3
"""
(c) PICKUP LOCATION ANALYSIS -- reducer.
OUTPUT: PULocationID \t trip_count
"""
import sys

cur, n = None, 0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    try:
        c = int(val)
    except ValueError:
        continue
    if key != cur:
        if cur is not None:
            print(f"{cur}\t{n}")
        cur, n = key, 0
    n += c
if cur is not None:
    print(f"{cur}\t{n}")
