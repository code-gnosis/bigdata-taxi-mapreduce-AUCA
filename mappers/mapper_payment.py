#!/usr/bin/env python3
"""
(e) PAYMENT METHOD ANALYSIS -- mapper.
KEY   = "1_Credit card" etc. Numeric prefix keeps TLC's own coding visible in the output
        while the label makes the result readable without the data dictionary to hand.
VALUE = "1,total,fare,tip"
"""
import sys

TYPES = {1: "Credit card", 2: "Cash", 3: "No charge", 4: "Dispute",
         5: "Unknown", 6: "Voided trip", 0: "Flex Fare"}

for line in sys.stdin:
    f = line.rstrip("\n").split("|")
    if len(f) < 14:
        continue
    try:
        pt = int(f[6]); total = float(f[10]); fare = float(f[7]); tip = float(f[8])
    except ValueError:
        continue
    print(f"{pt}_{TYPES.get(pt, 'Unknown')}\t1,{total:.2f},{fare:.2f},{tip:.2f}")
