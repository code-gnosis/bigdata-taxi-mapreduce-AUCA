#!/usr/bin/env python3
"""
MULTI-STAGE JOB -- STAGE 2 REDUCER.

Because stage 2's mapper inverted revenue into the key, records now arrive in DESCENDING
revenue order for free -- the framework's Shuffle and Sort did the ranking, not this code.
This reducer simply takes the first N and stops counting.

OUTPUT: rank \t zone \t trips \t revenue \t avg_fare \t avg_distance
"""
import sys

TOP_N = 10

rank = 0
for line in sys.stdin:
    _, _, val = line.rstrip("\n").partition("\t")
    parts = val.split(",")
    if len(parts) < 5:
        continue
    rank += 1
    if rank > TOP_N:
        break
    zone, trips, revenue, avg_fare, avg_dist = parts[:5]
    print(f"{rank}\t{zone}\t{trips}\t{revenue}\t{avg_fare}\t{avg_dist}")
