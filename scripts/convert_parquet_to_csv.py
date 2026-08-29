#!/usr/bin/env python3
"""
Convert NYC TLC monthly Parquet trip files to line-oriented CSV.

WHY THIS STEP EXISTS
--------------------
TLC publishes Parquet: columnar, compressed, splittable, schema-embedded -- ideal for
large-scale storage and for engines that push predicates into the file (Spark, Hive).
Hadoop Streaming, however, feeds each mapper RAW LINES on stdin. It has no Parquet reader.
So for a Streaming assignment the data must first be flattened to a line-oriented format.
The trade-off is size: CSV is uncompressed and repeats no schema, so it inflates ~10x.

Converted with a header row; the cleaning MapReduce job strips it (see mapper_clean.py).
"""
import glob, os, sys, time
import pyarrow.parquet as pq
import pyarrow.csv as pacsv
import pyarrow as pa

RAW = os.path.expanduser("~/taxi_project/data/raw_parquet")
OUT = os.path.expanduser("~/taxi_project/data/csv")
os.makedirs(OUT, exist_ok=True)

# Column order written to CSV -- fixed, because every mapper indexes positionally.
COLS = ["VendorID","tpep_pickup_datetime","tpep_dropoff_datetime","passenger_count",
        "trip_distance","RatecodeID","store_and_fwd_flag","PULocationID","DOLocationID",
        "payment_type","fare_amount","extra","mta_tax","tip_amount","tolls_amount",
        "improvement_surcharge","total_amount","congestion_surcharge","Airport_fee"]

total_rows = 0
t0 = time.time()

for src in sorted(glob.glob(f"{RAW}/*.parquet")):
    base = os.path.basename(src).replace(".parquet", ".csv")
    dst = os.path.join(OUT, base)
    pf = pq.ParquetFile(src)
    n = 0
    writer = None
    try:
        for batch in pf.iter_batches(batch_size=250_000, columns=COLS):
            tbl = pa.Table.from_batches([batch])
            # Timestamps -> ISO strings so mappers can parse them from text.
            for c in ("tpep_pickup_datetime", "tpep_dropoff_datetime"):
                tbl = tbl.set_column(tbl.schema.get_field_index(c), c,
                                     tbl.column(c).cast(pa.string()))
            if writer is None:
                writer = pacsv.CSVWriter(dst, tbl.schema)
            writer.write_table(tbl)
            n += tbl.num_rows
    finally:
        if writer is not None:
            writer.close()
    total_rows += n
    print(f"{base}: {n:,} rows -> {os.path.getsize(dst)/1e6:.0f} MB", flush=True)

print(f"\nTOTAL {total_rows:,} rows in {time.time()-t0:.0f}s")
