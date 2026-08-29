#!/usr/bin/env python3
"""
(g) BUSIEST PICKUP->DROPOFF ROUTES -- mapper.
KEY   = "PU->DO" composite. This is the assignment's "route key". Building a COMPOSITE KEY
        is the standard MapReduce technique for grouping on more than one field: you
        concatenate the fields into the key so the Shuffle groups on the pair.
        Cardinality here is up to 265 x 265 = 70,225 routes -- still small enough for one
        reducer, but far larger than the 24 keys of the hourly job.
VALUE = "1,total"
"""
import sys

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        pu = int(f[4]); do = int(f[5]); total = float(f[10])
    except ValueError:
        continue
    print(f"{pu:03d}->{do:03d}\t1,{total:.2f}")
