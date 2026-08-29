#!/usr/bin/env python3
"""
(h) TRIP DURATION ANALYSIS -- reducer.
OUTPUT: band \t trips, avg_fare, avg_distance, avg_tip, avg_duration, avg_speed_mph
avg_speed_mph is a derived sanity measure: implausible speeds flag meter or GPS problems.
"""
import sys

def flush(k, n, fare, dist, tip, dur):
    if k is None:
        return
    hours = dur / 60.0
    print(f"{k}\t{n}\t{fare/n if n else 0:.2f}\t{dist/n if n else 0:.2f}\t"
          f"{tip/n if n else 0:.2f}\t{dur/n if n else 0:.2f}\t{(dist/hours) if hours else 0:.2f}")

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
