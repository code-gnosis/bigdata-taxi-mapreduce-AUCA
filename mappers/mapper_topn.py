#!/usr/bin/env python3
"""
MULTI-STAGE JOB -- STAGE 2 MAPPER (consumes STAGE 1's HDFS output).

INPUT  : /taxi_project/output/revenue/part-*  (output of mapper_revenue + reducer_revenue)
         zone \t trips \t fare \t tips \t revenue \t avg_fare \t avg_distance

THE INVERTED-KEY TRICK
  MapReduce sorts by KEY, never by value. To rank zones by revenue we must therefore make
  revenue *the key*. But the sort is ascending lexical, so we:
     1. subtract the revenue from a large constant  -> descending order becomes ascending
     2. zero-pad to a fixed width                   -> lexical order becomes numeric order
  The original zone and its metrics ride along in the value. This is the standard
  "secondary sort by value" pattern in MapReduce, and it is why a second job is needed
  at all: stage 1 aggregates, stage 2 orders.

  Everything is routed to a SINGLE reducer (-numReduceTasks 1) because a global Top-N is
  meaningless if computed per-partition.
"""
import sys

BIG = 10**12   # larger than any plausible zone revenue, in cents

for line in sys.stdin:
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 7:
        continue
    zone = parts[0]
    try:
        trips = int(parts[1]); revenue = float(parts[4])
    except ValueError:
        continue
    inverted = BIG - int(round(revenue * 100))   # cents, to keep it integral
    print(f"{inverted:015d}\t{zone},{trips},{revenue:.2f},{parts[5]},{parts[6]}")
