#!/usr/bin/env python3
"""
(b) DAILY DEMAND -- mapper.
KEY   = "0_Monday" .. "6_Sunday". The numeric prefix forces calendar order through the
        lexical sort; the name is carried along so the output is human-readable.
VALUE = "1,total_revenue,is_weekend"
"""
import sys

NAMES = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        dow, total = int(f[12]), float(f[10])
    except ValueError:
        continue
    if not 0 <= dow <= 6:
        continue
    print(f"{dow}_{NAMES[dow]}\t1,{total:.2f},{1 if dow >= 5 else 0}")
