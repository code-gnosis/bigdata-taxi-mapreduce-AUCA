#!/usr/bin/env python3
"""
(i) ANOMALY DETECTION -- reducer.
OUTPUT: anomaly_type \t count
Categories overlap by design (one record can trip several rules), so these counts
must not be added together to form a total. The CLEAN count is the honest denominator.
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
