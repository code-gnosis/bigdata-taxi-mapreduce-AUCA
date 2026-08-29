#!/bin/bash
# =============================================================================
#  Distributed Taxi Trip Analytics -- full Hadoop Streaming job sequence
#  Run from ~/taxi_project  (a SPACE-FREE path: Hadoop parses -files args as URIs
#  and any space raises java.net.URISyntaxException)
# =============================================================================
set -u
cd ~/taxi_project
STREAM_JAR=$(ls /opt/homebrew/opt/hadoop/libexec/share/hadoop/tools/lib/hadoop-streaming-*.jar)
LOGS=~/taxi_project/evidence
mkdir -p "$LOGS"

run_job () {
  local name=$1 in=$2 out=$3 mapper=$4 reducer=$5 nred=$6
  echo ""
  echo "############ JOB: $name ############"
  hdfs dfs -rm -r -skipTrash "$out" >/dev/null 2>&1     # MapReduce refuses to overwrite
  local t0=$(date +%s)
  if [ "$reducer" = "NONE" ]; then
    hadoop jar "$STREAM_JAR" \
      -files "mappers/$mapper" \
      -input "$in" -output "$out" \
      -mapper "$mapper" -numReduceTasks 0 > "$LOGS/${name}.log" 2>&1
  else
    hadoop jar "$STREAM_JAR" \
      -files "mappers/$mapper,reducers/$reducer" \
      -input "$in" -output "$out" \
      -mapper "$mapper" -reducer "$reducer" -numReduceTasks "$nred" \
      > "$LOGS/${name}.log" 2>&1
  fi
  local rc=$? t1=$(date +%s)
  echo "$name elapsed=$((t1-t0))s rc=$rc"
  echo "$name,$((t1-t0)),$rc" >> "$LOGS/timings.csv"
  grep -E "Submitted application|Job job_.* completed|Streaming Command Failed" "$LOGS/${name}.log" | head -3
  return $rc
}

echo "job,seconds,rc" > "$LOGS/timings.csv"

# ---- STAGE 1: cleaning + de-duplication (raw -> cleaned) --------------------
run_job clean /taxi_project/input/raw /taxi_project/input/cleaned \
        mapper_clean.py reducer_clean.py 4 || exit 1

# ---- The eight required analyses -------------------------------------------
run_job hourly   /taxi_project/input/cleaned /taxi_project/output/hourly    mapper_hourly.py   reducer_hourly.py   1
run_job daily    /taxi_project/input/cleaned /taxi_project/output/daily     mapper_daily.py    reducer_daily.py    1
run_job location /taxi_project/input/cleaned /taxi_project/output/locations mapper_location.py reducer_location.py 1
run_job revenue  /taxi_project/input/cleaned /taxi_project/output/revenue   mapper_revenue.py  reducer_revenue.py  1
run_job payment  /taxi_project/input/cleaned /taxi_project/output/payment   mapper_payment.py  reducer_payment.py  1
run_job distance /taxi_project/input/cleaned /taxi_project/output/distance  mapper_distance.py reducer_distance.py 1
run_job duration /taxi_project/input/cleaned /taxi_project/output/duration  mapper_duration.py reducer_duration.py 1
run_job route    /taxi_project/input/cleaned /taxi_project/output/routes    mapper_route.py    reducer_route.py    2

# ---- Anomaly detection runs on RAW, by design ------------------------------
run_job anomaly  /taxi_project/input/raw     /taxi_project/output/anomalies mapper_anomaly.py  reducer_anomaly.py  1

# ---- MULTI-STAGE: stage 2 consumes stage 1's HDFS output -------------------
# Single reducer: a global Top-N is meaningless computed per-partition.
run_job topn_revenue /taxi_project/output/revenue /taxi_project/output/top10_revenue \
        mapper_topn.py reducer_topn.py 1

echo ""
echo "############ ALL JOBS DONE ############"
cat "$LOGS/timings.csv"
