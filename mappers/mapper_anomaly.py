#!/usr/bin/env python3
"""
(i) ANOMALY DETECTION -- mapper.

Runs against the RAW data, not the cleaned data. That is the whole point: the cleaning job
already removed hard-invalid records, so anomalies must be measured against the original
input to state what percentage of the source was suspicious.

KEY   = anomaly type (or "0_CLEAN" for records that trip no rule)
VALUE = "1"
A single record can trip several rules, so it is emitted once per rule -- the category
counts therefore overlap and must not be summed to a total. The report says so explicitly.
"""
import sys
import csv
from datetime import datetime

C_PICKUP, C_DROPOFF, C_PASSENGERS, C_DISTANCE = 1, 2, 3, 4
C_FARE, C_TOTAL = 10, 16
TS = "%Y-%m-%d %H:%M:%S"

def parse_ts(v):
    try:
        return datetime.strptime(v.split(".")[0], TS)
    except (ValueError, AttributeError):
        return None

for row in csv.reader(sys.stdin):
    if not row or row[0] == "VendorID" or len(row) < 19:
        continue
    flagged = False
    try:
        dist = float(row[C_DISTANCE]); fare = float(row[C_FARE]); total = float(row[C_TOTAL])
        pax  = int(float(row[C_PASSENGERS])) if row[C_PASSENGERS] else -1
    except (ValueError, IndexError):
        print("9_UNPARSEABLE_NUMERIC\t1")
        continue

    if dist <= 0:                    print("1_ZERO_OR_NEG_DISTANCE\t1"); flagged = True
    if dist > 200:                   print("2_EXTREME_DISTANCE\t1");     flagged = True
    if fare <= 0:                    print("3_ZERO_OR_NEG_FARE\t1");     flagged = True
    if fare > 1000:                  print("4_EXTREME_FARE\t1");         flagged = True
    if pax < 1 or pax > 8:           print("5_INVALID_PASSENGER_COUNT\t1"); flagged = True
    if total < 0:                    print("6_NEGATIVE_TOTAL\t1");       flagged = True

    p, d = parse_ts(row[C_PICKUP]), parse_ts(row[C_DROPOFF])
    if p is None or d is None:
        print("7_BAD_TIMESTAMP\t1"); flagged = True
    else:
        mins = (d - p).total_seconds() / 60.0
        if mins <= 0 or mins > 1440:
            print("8_IMPOSSIBLE_DURATION\t1"); flagged = True
        # fare-per-mile is the classic meter-fraud signal
        if dist > 0 and fare > 0:
            fpm = fare / dist
            if fpm > 100:
                print("A_EXTREME_FARE_PER_MILE\t1"); flagged = True

    if not flagged:
        print("0_CLEAN\t1")
