#!/usr/bin/env python3
"""
(c) PICKUP LOCATION ANALYSIS -- mapper.
KEY   = PULocationID (zero-padded to 3 so sort order is numeric).
VALUE = "1" -- a pure count. Top-10 / Bottom-10 ranking is NOT done here: ranking is a
        global operation and a mapper only sees its own split. Ranking happens in the
        second stage of the multi-stage job (mapper_topn / reducer_topn).
"""
import sys

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        pu = int(f[4])
    except ValueError:
        continue
    print(f"{pu:03d}\t1")
