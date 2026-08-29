#!/usr/bin/env python3
"""
STAGE 1 REDUCER -- De-duplication.

INPUT  : dedup_key \t cleaned_record, sorted by key (guaranteed by Shuffle and Sort)
OUTPUT : cleaned_record only -- the key is dropped, because downstream jobs want plain
         pipe-delimited data, not a keyed stream.

WHY THIS WORKS
  Shuffle and Sort guarantees two things this reducer depends on absolutely:
    1. every record sharing a dedup_key arrives at the SAME reducer, and
    2. those records arrive CONSECUTIVELY.
  So "have I seen this key before?" collapses to "is this key the same as the previous line?"
  -- an O(1) memory check rather than holding millions of keys in a set. This is the single
  most important idea in reducer design: the sort does the grouping work for you.
"""
import sys

def counter(name, n=1):
    sys.stderr.write(f"reporter:counter:Cleaning,{name},{n}\n")

def main():
    current_key = None
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        key, _, record = line.partition("\t")
        if key == current_key:
            counter("duplicates_removed")     # same trip fingerprint as the previous line
            continue
        current_key = key
        counter("unique_records_written")
        print(record)

if __name__ == "__main__":
    main()
