#!/usr/bin/env python3
"""
STAGE 1 MAPPER -- Data cleaning and validation.

INPUT  : raw TLC CSV lines from /taxi_project/input/raw/  (header row present in one split only)
OUTPUT : dedup_key \t cleaned_record
         The reducer collapses identical dedup_keys, which is how duplicates are removed.

KEY-VALUE DESIGN
  key   = a composite fingerprint of the trip (pickup ts, dropoff ts, PU, DO, distance, fare).
          TLC records carry no trip ID, so this composite IS the identity of a trip.
          Sending identical trips to the same reducer is what makes de-duplication possible.
  value = the normalised, validated record with three derived fields appended.

REJECTIONS ARE COUNTED, NOT SILENTLY DROPPED.
  Every discarded record increments a Hadoop counter via stderr:
      reporter:counter:<group>,<name>,<increment>
  Those counters appear in the job summary, which is how the report states exactly how many
  records failed each rule and what percentage of the dataset that represents.

HEADER SAFETY
  Hadoop splits the file across mappers; only the split containing byte 0 sees the header row.
  Every other mapper receives data rows only. So the header cannot be consumed positionally --
  it is detected by content ("VendorID") and skipped wherever it lands.
"""
import sys
import csv
from datetime import datetime

# Raw TLC column positions (fixed by scripts/convert_parquet_to_csv.py).
C_PICKUP, C_DROPOFF, C_PASSENGERS, C_DISTANCE = 1, 2, 3, 4
C_PU, C_DO, C_PAYMENT = 7, 8, 9
C_FARE, C_TIP, C_TOLLS, C_TOTAL = 10, 13, 14, 16

TS = "%Y-%m-%d %H:%M:%S"

# Validity bounds. Chosen from the TLC data dictionary and basic physical plausibility,
# and justified individually in the report -- not arbitrary.
MAX_PASSENGERS   = 8       # legal capacity of an NYC yellow cab
MAX_DISTANCE_MI  = 200.0   # beyond this is out of the metro area entirely
MAX_FARE         = 1000.0
MIN_DURATION_MIN = 1.0     # a "trip" under 60s is a meter error, not a journey
MAX_DURATION_MIN = 1440.0  # 24 hours
DATA_START = datetime(2024, 1, 1)
DATA_END   = datetime(2024, 4, 1)   # exclusive: we loaded Jan/Feb/Mar 2024


def counter(name, n=1):
    """Emit a Hadoop counter increment. stderr is the control channel; stdout is data."""
    sys.stderr.write(f"reporter:counter:Cleaning,{name},{n}\n")


def parse_ts(value):
    """TLC timestamps arrive as 'YYYY-MM-DD HH:MM:SS', sometimes with fractional seconds."""
    try:
        return datetime.strptime(value.split(".")[0], TS)
    except (ValueError, AttributeError):
        return None


def main():
    for row in csv.reader(sys.stdin):
        counter("records_read")

        # --- structural checks -------------------------------------------------
        if not row:
            counter("rejected_empty_line")
            continue
        if row[0] == "VendorID":            # header row, wherever it lands
            counter("header_rows_skipped")
            continue
        if len(row) < 19:
            counter("rejected_wrong_field_count")
            continue

        # --- timestamps --------------------------------------------------------
        pickup, dropoff = parse_ts(row[C_PICKUP]), parse_ts(row[C_DROPOFF])
        if pickup is None or dropoff is None:
            counter("rejected_unparseable_timestamp")
            continue
        if dropoff <= pickup:
            counter("rejected_dropoff_before_pickup")
            continue
        if not (DATA_START <= pickup < DATA_END):
            # TLC files habitually contain a few stray records from other years.
            counter("rejected_timestamp_out_of_range")
            continue

        duration_min = (dropoff - pickup).total_seconds() / 60.0
        if duration_min < MIN_DURATION_MIN or duration_min > MAX_DURATION_MIN:
            counter("rejected_impossible_duration")
            continue

        # --- numeric fields ----------------------------------------------------
        try:
            passengers = int(float(row[C_PASSENGERS])) if row[C_PASSENGERS] else -1
            distance   = float(row[C_DISTANCE])
            fare       = float(row[C_FARE])
            tip        = float(row[C_TIP])
            tolls      = float(row[C_TOLLS])
            total      = float(row[C_TOTAL])
            pu, do     = int(row[C_PU]), int(row[C_DO])
            payment    = int(float(row[C_PAYMENT])) if row[C_PAYMENT] else 0
        except (ValueError, IndexError):
            counter("rejected_missing_or_nonnumeric")
            continue

        if passengers < 1 or passengers > MAX_PASSENGERS:
            counter("rejected_invalid_passenger_count")
            continue
        if distance <= 0 or distance > MAX_DISTANCE_MI:
            counter("rejected_invalid_distance")
            continue
        if fare <= 0 or fare > MAX_FARE:
            counter("rejected_invalid_fare")
            continue
        if total <= 0:
            counter("rejected_invalid_total")
            continue
        if tip < 0 or tolls < 0:
            counter("rejected_negative_tip_or_tolls")
            continue
        if not (1 <= pu <= 265) or not (1 <= do <= 265):
            counter("rejected_invalid_zone_id")
            continue

        # --- emit --------------------------------------------------------------
        # Derived fields (hour, day-of-week, duration) are computed ONCE here so that the
        # eight downstream analysis mappers never re-parse a timestamp. This is a deliberate
        # denormalisation: it trades a little output width for CPU across every later job.
        hour = pickup.hour
        dow  = pickup.weekday()          # Monday=0 .. Sunday=6

        record = "|".join([
            pickup.strftime(TS), dropoff.strftime(TS), str(passengers),
            f"{distance:.2f}", str(pu), str(do), str(payment),
            f"{fare:.2f}", f"{tip:.2f}", f"{tolls:.2f}", f"{total:.2f}",
            str(hour), str(dow), f"{duration_min:.2f}",
        ])

        dedup_key = f"{pickup.strftime(TS)}|{dropoff.strftime(TS)}|{pu}|{do}|{distance:.2f}|{fare:.2f}"
        counter("records_passed_validation")
        print(f"{dedup_key}\t{record}")


if __name__ == "__main__":
    main()
