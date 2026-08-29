# Distributed Taxi Trip Analytics — Hadoop, HDFS and Python MapReduce

**Course:** Big Data Essentials (MSc Big Data Analytics, AUCA)
**Assignment:** Individual Practical Case Study
**Dataset:** NYC Taxi & Limousine Commission — Yellow Taxi Trip Records, January–March 2024
**Scale:** 9,554,778 raw trip records · 1.02 GB as CSV · 153 MB as source Parquet

---

## 1. What this project does

Processes three months of NYC yellow-taxi trip records with Hadoop MapReduce, using HDFS
for distributed storage and Hadoop Streaming so that all mappers and reducers are ordinary
Python programs reading `stdin` and writing `stdout`.

Nine analyses are produced — hourly demand, daily demand, pickup-zone counts, revenue by
zone, payment behaviour, distance-band economics, busiest routes, trip-duration bands and
anomaly detection — plus a compulsory two-stage MapReduce workflow and a like-for-like
performance comparison against single-machine Pandas.

---

## 2. Environment

| Component | Version |
|---|---|
| OS | macOS 26.5.2 (Tahoe), Apple M4 (arm64) |
| Hadoop | 3.5.0 (Homebrew), pseudo-distributed |
| Java | OpenJDK 17.0.20 |
| Python | 3.14 (mappers/reducers use only the standard library) |
| Python (analysis) | 3.12 venv — pandas, pyarrow, matplotlib |

### HDFS configuration (`core-site.xml`)

```xml
<property><name>fs.defaultFS</name><value>hdfs://localhost:8020</value></property>
<property><name>hadoop.tmp.dir</name><value>/Users/thierrys/hadoop-data</value></property>
```

Two deliberate departures from the common tutorial defaults:

- **Port 8020 rather than 9000.** 9000 was already bound by another local process. 8020 is
  Hadoop 3's own default, so nothing is lost.
- **`hadoop.tmp.dir` moved off `/tmp`.** Hadoop defaults HDFS storage to `/tmp`, which
  macOS clears periodically. When that happened during development the NameNode failed with
  `InconsistentFSStateException: Directory .../dfs/name is in an inconsistent state` and the
  entire filesystem had to be reformatted. Storage now lives in the home directory and
  survives reboots.

### YARN configuration note

`yarn.nodemanager.env-whitelist` must include `PATH`. Without it, the environment inside a
YARN container has no `/opt/homebrew/bin`, so the `#!/usr/bin/env python3` shebang on every
mapper fails to resolve and each task dies with *python3: No such file or directory*.

---

## 3. Repository layout

```
taxi_project/
├── mappers/                  # 10 mapper programs + SCHEMA.md
├── reducers/                 # 10 reducer programs
├── scripts/
│   ├── convert_parquet_to_csv.py   # TLC Parquet -> line-oriented CSV
│   ├── run_all_jobs.sh             # full job sequence, with timings
│   ├── pandas_benchmark.py         # single-machine comparison (Section 12)
│   └── make_visualizations.py      # the seven required charts
├── evidence/                 # per-job Hadoop console logs + timings.csv
├── output/local/             # results pulled back out of HDFS
├── report/figures/           # generated PNG charts
├── commands.txt              # every command, in order
└── README.md
```

---

## 4. How to reproduce

```bash
# 1. Environment
export HADOOP_HOME=/opt/homebrew/opt/hadoop/libexec
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
start-dfs.sh && start-yarn.sh && jps

# 2. Data
bash scripts/download_data.sh          # or see commands.txt section 2
python3 scripts/convert_parquet_to_csv.py

# 3. Load into HDFS
hdfs dfs -mkdir -p /taxi_project/input/raw
hdfs dfs -put data/csv/yellow_tripdata_*.csv /taxi_project/input/raw/

# 4. Run every MapReduce job (cleaning -> 9 analyses -> multi-stage)
./scripts/run_all_jobs.sh

# 5. Comparison + charts
python3 scripts/pandas_benchmark.py
python3 scripts/make_visualizations.py
```

**Run from a path with no spaces.** Hadoop parses `-files` arguments as URIs, and a space
anywhere in the path raises `java.net.URISyntaxException: Illegal character in path`.

---

## 5. Design decisions worth knowing

**Cleaning is a full MapReduce job, not a pre-processing script.** The mapper validates and
normalises; the reducer de-duplicates. De-duplication *requires* a reducer, because
identifying a duplicate means comparing records that may sit in different input splits — only
the shuffle can bring them together.

**The cleaned record carries three derived fields** (`hour`, `dayofweek`, `duration_min`)
computed once at clean time. The eight analysis mappers therefore never parse a timestamp:
a deliberate denormalisation that trades output width for CPU across every downstream job.

**No header row in the cleaned data.** Hadoop splits input across mappers and only the split
containing byte 0 sees the header. Any mapper relying on `csv.DictReader(stdin)` without
explicit `fieldnames` would treat a data row as the header and fail with `KeyError`. The
cleaning stage removes the header entirely and the schema is documented in `mappers/SCHEMA.md`.

**Mapper values are partial aggregates, not bare `1`s.** Emitting `"1,fare,tip,total,distance"`
lets one shuffle carry five measures instead of five, and lets the same reducer double as a
combiner unchanged.

**Keys are padded and prefixed for ordering.** MapReduce sorts keys lexically, so hours are
`"00".."23"` and bands are `"1_0-2mi".."5_20+mi"`. Unpadded, `10` would sort before `2`.

**Rejections are counted, never silent.** Every discarded record increments a Hadoop counter
via `reporter:counter:Cleaning,<rule>,1` on stderr, so the report can state exactly how many
records failed each rule and why.

---

## 6. Results summary

See `report/` for the full analysis. Headline findings and the answers to the twelve business
questions in Section 15 of the brief are in the final report.
