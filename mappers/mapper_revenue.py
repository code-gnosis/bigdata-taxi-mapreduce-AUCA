#!/usr/bin/env python3
"""
(d) REVENUE BY PICKUP LOCATION -- mapper.  Also STAGE 1 of the multi-stage workflow.

KEY   = PULocationID (3-padded).
VALUE = "1,fare,tip,total,distance" -- five partial aggregates in one value.

WHY PACK FIVE MEASURES INTO ONE VALUE rather than emit five key-value pairs?
Every emitted pair costs a shuffle. Packing them means one shuffle carries all five
measures, cutting intermediate data ~5x. This is the main lever you have on MapReduce
performance: reduce what crosses the network between map and reduce.
"""
import sys

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        pu = int(f[4]); dist = float(f[3]); fare = float(f[7])
        tip = float(f[8]); total = float(f[10])
    except ValueError:
        continue
    print(f"{pu:03d}\t1,{fare:.2f},{tip:.2f},{total:.2f},{dist:.2f}")
