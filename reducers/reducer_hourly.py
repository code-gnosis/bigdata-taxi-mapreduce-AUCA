#!/usr/bin/env python3
"""
(a) HOURLY TAXI DEMAND -- reducer.

Relies on the Shuffle-and-Sort contract: all values for one hour arrive together and
consecutively. We therefore accumulate while the key is unchanged and flush on key change.
OUTPUT: hour \t trips, total_fare, total_revenue, avg_fare
"""
import sys

def flush(key, trips, fare, revenue):
    if key is not None:
        avg = fare / trips if trips else 0.0
        print(f"{key}\t{trips}\t{fare:.2f}\t{revenue:.2f}\t{avg:.2f}")

cur, n, sf, sr = None, 0, 0.0, 0.0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    try:
        c, fare, total = val.split(",")
        c, fare, total = int(c), float(fare), float(total)
    except ValueError:
        continue
    if key != cur:
        flush(cur, n, sf, sr)
        cur, n, sf, sr = key, 0, 0.0, 0.0
    n += c; sf += fare; sr += total
flush(cur, n, sf, sr)
