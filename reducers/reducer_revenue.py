#!/usr/bin/env python3
"""
(d) REVENUE BY PICKUP LOCATION -- reducer.
OUTPUT: PULocationID \t trips, total_fare, total_tips, total_revenue, avg_fare, avg_distance
This output becomes the INPUT to stage 2 of the multi-stage job (top-10 by revenue).
"""
import sys

def flush(k, n, fare, tip, tot, dist):
    if k is None:
        return
    print(f"{k}\t{n}\t{fare:.2f}\t{tip:.2f}\t{tot:.2f}\t{fare/n if n else 0:.2f}\t{dist/n if n else 0:.2f}")

cur, n, sfare, stip, stot, sdist = None, 0, 0.0, 0.0, 0.0, 0.0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    try:
        c, fare, tip, tot, dist = val.split(",")
        c = int(c); fare = float(fare); tip = float(tip); tot = float(tot); dist = float(dist)
    except ValueError:
        continue
    if key != cur:
        flush(cur, n, sfare, stip, stot, sdist)
        cur, n, sfare, stip, stot, sdist = key, 0, 0.0, 0.0, 0.0, 0.0
    n += c; sfare += fare; stip += tip; stot += tot; sdist += dist
flush(cur, n, sfare, stip, stot, sdist)
