#!/usr/bin/env python3
"""
(e) PAYMENT METHOD ANALYSIS -- reducer.
OUTPUT: payment_type \t trips, revenue, avg_fare, avg_tip, tip_pct_of_fare
tip_pct_of_fare is what answers "do credit-card users generate more tips?" -- cash tips
are not recorded by the meter, so the expected finding is a near-zero cash tip rate.
"""
import sys

def flush(k, n, rev, fare, tip):
    if k is None:
        return
    print(f"{k}\t{n}\t{rev:.2f}\t{fare/n if n else 0:.2f}\t{tip/n if n else 0:.2f}\t{(tip/fare*100) if fare else 0:.2f}")

cur, n, srev, sfare, stip = None, 0, 0.0, 0.0, 0.0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    try:
        c, total, fare, tip = val.split(",")
        c = int(c); total = float(total); fare = float(fare); tip = float(tip)
    except ValueError:
        continue
    if key != cur:
        flush(cur, n, srev, sfare, stip)
        cur, n, srev, sfare, stip = key, 0, 0.0, 0.0, 0.0
    n += c; srev += total; sfare += fare; stip += tip
flush(cur, n, srev, sfare, stip)
