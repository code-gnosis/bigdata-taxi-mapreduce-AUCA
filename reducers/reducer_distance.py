#!/usr/bin/env python3
"""
(f) DISTANCE-BASED FARE ANALYSIS -- reducer.
OUTPUT: band \t trips, avg_fare, avg_distance, avg_tip, avg_duration_min, fare_per_mile
"""
import sys

def flush(k, n, fare, dist, tip, dur):
    if k is None:
        return
    print(f"{k}\t{n}\t{fare/n if n else 0:.2f}\t{dist/n if n else 0:.2f}\t"
          f"{tip/n if n else 0:.2f}\t{dur/n if n else 0:.2f}\t{(fare/dist) if dist else 0:.2f}")

cur, n, sf, sd, st, sdur = None, 0, 0.0, 0.0, 0.0, 0.0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    try:
        c, fare, dist, tip, dur = val.split(",")
        c = int(c); fare = float(fare); dist = float(dist); tip = float(tip); dur = float(dur)
    except ValueError:
        continue
    if key != cur:
        flush(cur, n, sf, sd, st, sdur)
        cur, n, sf, sd, st, sdur = key, 0, 0.0, 0.0, 0.0, 0.0
    n += c; sf += fare; sd += dist; st += tip; sdur += dur
flush(cur, n, sf, sd, st, sdur)
