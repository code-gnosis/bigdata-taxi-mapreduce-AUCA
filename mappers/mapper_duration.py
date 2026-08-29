#!/usr/bin/env python3
"""
(h) TRIP DURATION ANALYSIS -- mapper.
Duration was computed once during cleaning (field 13), so this mapper does no datetime
parsing at all -- it only bins. That is the payoff of denormalising at clean time.
KEY   = duration band (numerically prefixed for ordering)
VALUE = "1,fare,distance,tip,duration"
"""
import sys

def band(m):
    if m <= 5:   return "1_0-5min"
    if m <= 15:  return "2_5-15min"
    if m <= 30:  return "3_15-30min"
    if m <= 60:  return "4_30-60min"
    return "5_60min+"

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        dur = float(f[13]); fare = float(f[7]); dist = float(f[3]); tip = float(f[8])
    except ValueError:
        continue
    print(f"{band(dur)}\t1,{fare:.2f},{dist:.2f},{tip:.2f},{dur:.2f}")
