#!/usr/bin/env python3
"""
(b) DAILY DEMAND -- reducer.
OUTPUT: day \t trips, revenue, avg_revenue_per_trip, WEEKDAY|WEEKEND
Also prints a weekday-vs-weekend summary block at the end, which answers the
"compare weekday versus weekend demand" part of the requirement directly.
"""
import sys

def flush(key, n, rev, wknd):
    if key is None:
        return
    avg = rev / n if n else 0.0
    print(f"{key}\t{n}\t{rev:.2f}\t{avg:.2f}\t{'WEEKEND' if wknd else 'WEEKDAY'}")

cur, n, rev, wknd = None, 0, 0.0, 0
wd_trips = wd_rev = we_trips = we_rev = 0
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t")
    try:
        c, total, is_we = val.split(",")
        c, total, is_we = int(c), float(total), int(is_we)
    except ValueError:
        continue
    if key != cur:
        flush(cur, n, rev, wknd)
        cur, n, rev, wknd = key, 0, 0.0, is_we
    n += c; rev += total; wknd = is_we
    if is_we: we_trips += c; we_rev += total
    else:     wd_trips += c; wd_rev += total
flush(cur, n, rev, wknd)

print(f"SUMMARY_WEEKDAY\t{wd_trips}\t{wd_rev:.2f}\t{wd_rev/wd_trips if wd_trips else 0:.2f}\tWEEKDAY")
print(f"SUMMARY_WEEKEND\t{we_trips}\t{we_rev:.2f}\t{we_rev/we_trips if we_trips else 0:.2f}\tWEEKEND")
