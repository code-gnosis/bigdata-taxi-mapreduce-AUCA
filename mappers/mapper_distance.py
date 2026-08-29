#!/usr/bin/env python3
"""
(f) DISTANCE-BASED FARE ANALYSIS -- mapper.
KEY   = distance band, numerically prefixed so bands sort in ascending distance order.
        Binning happens in the MAPPER, not the reducer: it turns 9.5M distinct float
        distances into 5 keys, which is a ~2-million-fold reduction in shuffle cardinality.
VALUE = "1,fare,distance,tip,duration"
"""
import sys

def band(d):
    if d <= 2:   return "1_0-2mi"
    if d <= 5:   return "2_2-5mi"
    if d <= 10:  return "3_5-10mi"
    if d <= 20:  return "4_10-20mi"
    return "5_20+mi"

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        dist = float(f[3]); fare = float(f[7]); tip = float(f[8]); dur = float(f[13])
    except ValueError:
        continue
    print(f"{band(dist)}\t1,{fare:.2f},{dist:.2f},{tip:.2f},{dur:.2f}")
