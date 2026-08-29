#!/usr/bin/env python3
"""
SECTION 12 -- PERFORMANCE COMPARISON (compulsory)

Runs the IDENTICAL analysis as the Hadoop `hourly` job -- trips and revenue grouped by
hour of pickup -- using conventional single-machine Python/Pandas, and records wall-clock
time and peak memory so the two approaches can be compared on equal terms.

Fairness notes (stated in the report):
  * Both read the same 1.02 GB of CSV and apply the same validity filters.
  * Pandas reads from the LOCAL filesystem; Hadoop reads from HDFS. Hadoop therefore
    carries extra cost that Pandas does not -- JVM startup, container allocation, HDFS
    reads and a disk-based shuffle. On one laptop that overhead dominates, which is
    precisely the finding the report is meant to explain.
"""
import os, time, glob, resource
import pandas as pd

CSV = os.path.expanduser("~/taxi_project/data/csv")
COLS = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count",
        "trip_distance", "fare_amount", "total_amount"]

t0 = time.time()
rows_read = 0
frames = []

for f in sorted(glob.glob(f"{CSV}/*.csv")):
    # chunked read: loading 9.5M rows x 19 cols at once would exhaust RAM on a 16GB laptop,
    # which is itself part of the finding.
    for chunk in pd.read_csv(f, usecols=COLS, chunksize=500_000):
        rows_read += len(chunk)
        chunk["tpep_pickup_datetime"]  = pd.to_datetime(chunk["tpep_pickup_datetime"], errors="coerce")
        chunk["tpep_dropoff_datetime"] = pd.to_datetime(chunk["tpep_dropoff_datetime"], errors="coerce")
        dur = (chunk["tpep_dropoff_datetime"] - chunk["tpep_pickup_datetime"]).dt.total_seconds() / 60
        # same validity rules as mapper_clean.py
        m = (
            chunk["tpep_pickup_datetime"].notna() & chunk["tpep_dropoff_datetime"].notna()
            & chunk["passenger_count"].between(1, 8)
            & (chunk["trip_distance"] > 0) & (chunk["trip_distance"] <= 200)
            & (chunk["fare_amount"] > 0) & (chunk["fare_amount"] <= 1000)
            & (chunk["total_amount"] > 0)
            & dur.between(1, 1440)
            & (chunk["tpep_pickup_datetime"] >= "2024-01-01")
            & (chunk["tpep_pickup_datetime"] <  "2024-04-01")
        )
        c = chunk[m].copy()
        c["hour"] = c["tpep_pickup_datetime"].dt.hour
        frames.append(c.groupby("hour").agg(
            trips=("fare_amount", "size"),
            total_fare=("fare_amount", "sum"),
            total_revenue=("total_amount", "sum"),
        ))

combined = pd.concat(frames).groupby(level=0).sum()
combined["avg_fare"] = combined["total_fare"] / combined["trips"]
elapsed = time.time() - t0
peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)  # macOS reports bytes

out = os.path.expanduser("~/taxi_project/output/pandas_hourly.tsv")
combined.to_csv(out, sep="\t")

print(f"rows_read       : {rows_read:,}")
print(f"rows_after_clean: {int(combined['trips'].sum()):,}")
print(f"elapsed_seconds : {elapsed:.1f}")
print(f"peak_memory_MB  : {peak_mb:.0f}")
print(f"output          : {out}")
print()
print(combined.head(24).to_string())
