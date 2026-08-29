#!/usr/bin/env python3
"""
SECTION 14 -- REQUIRED VISUALIZATIONS

Reads the MapReduce results that were pulled out of HDFS into ~/taxi_project/output/local/
and renders the seven required charts into report/figures/.

The zone lookup table (taxi_zone_lookup.csv) maps LocationID -> human-readable zone name,
so charts name neighbourhoods rather than opaque integers.
"""
import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.expanduser("~/taxi_project")
LOCAL = f"{BASE}/output/local"
FIG = f"{BASE}/report/figures"
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True,
                     "grid.alpha": .3, "axes.axisbelow": True})
BLUE, GREEN, ORANGE = "#2b6cb0", "#2f855a", "#c05621"

zones = {}
with open(f"{BASE}/data/taxi_zone_lookup.csv") as fh:
    for r in csv.DictReader(fh):
        zones[int(r["LocationID"])] = f'{r["Zone"]} ({r["Borough"]})'

def read(name):
    """Read a MapReduce part-file result as a list of tab-split rows."""
    p = f"{LOCAL}/{name}.tsv"
    if not os.path.exists(p):
        print(f"  !! missing {p}")
        return []
    with open(p) as fh:
        return [ln.rstrip("\n").split("\t") for ln in fh if ln.strip()]

def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"{FIG}/{name}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}.png")

# --- 1. Trips by hour --------------------------------------------------------
rows = sorted(read("hourly"), key=lambda r: r[0])
if rows:
    hrs = [int(r[0]) for r in rows]; trips = [int(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(hrs, trips, color=BLUE)
    peak = trips.index(max(trips)); low = trips.index(min(trips))
    bars[peak].set_color(ORANGE); bars[low].set_color("#a0aec0")
    ax.set(xlabel="Hour of day", ylabel="Trips",
           title="Taxi demand by hour of day (NYC yellow cabs, Jan-Mar 2024)")
    ax.set_xticks(range(0, 24))
    ax.set_ylim(0, max(trips) * 1.13)          # headroom so annotations don't clip
    ax.annotate(f"busiest: {hrs[peak]:02d}:00", (hrs[peak], trips[peak]),
                textcoords="offset points", xytext=(0, 6), ha="center", color=ORANGE, fontweight="bold")
    ax.annotate(f"quietest: {hrs[low]:02d}:00", (hrs[low], trips[low]),
                textcoords="offset points", xytext=(0, 6), ha="center", color="#4a5568")
    save(fig, "01_trips_by_hour")

# --- 2. Trips by day of week -------------------------------------------------
rows = [r for r in read("daily") if not r[0].startswith("SUMMARY")]
rows.sort(key=lambda r: r[0])
if rows:
    names = [r[0].split("_", 1)[1] for r in rows]; trips = [int(r[1]) for r in rows]
    cols = [ORANGE if r[4] == "WEEKEND" else BLUE for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(names, trips, color=cols)
    ax.set(ylabel="Trips", title="Taxi demand by day of week (orange = weekend)")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    save(fig, "02_trips_by_day")

# --- 3. Top 10 pickup zones --------------------------------------------------
rows = sorted(read("locations"), key=lambda r: -int(r[1]))[:10]
if rows:
    labels = [zones.get(int(r[0]), r[0])[:34] for r in rows][::-1]
    vals = [int(r[1]) for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(labels, vals, color=BLUE)
    ax.set(xlabel="Trips", title="Top 10 pickup zones by trip count")
    save(fig, "03_top10_pickup_zones")

# --- 4. Revenue by payment method --------------------------------------------
rows = read("payment")
if rows:
    rows = sorted(rows, key=lambda r: -float(r[2]))
    labels = [r[0].split("_", 1)[1] for r in rows]; rev = [float(r[2]) for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    a1.bar(labels, rev, color=GREEN)
    a1.set(ylabel="Total revenue (USD)", title="Revenue by payment method")
    plt.setp(a1.get_xticklabels(), rotation=20, ha="right")
    tip_pct = [float(r[5]) for r in rows]
    a2.bar(labels, tip_pct, color=ORANGE)
    a2.set(ylabel="Tip as % of fare", title="Tip rate by payment method\n(cash tips are not metered)")
    plt.setp(a2.get_xticklabels(), rotation=20, ha="right")
    save(fig, "04_revenue_by_payment")

# --- 5. Trips by distance category -------------------------------------------
rows = sorted(read("distance"), key=lambda r: r[0])
if rows:
    labels = [r[0].split("_", 1)[1] for r in rows]
    trips = [int(r[1]) for r in rows]; fpm = [float(r[6]) for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    a1.bar(labels, trips, color=BLUE); a1.set(ylabel="Trips", title="Trips by distance band")
    a2.plot(labels, fpm, "o-", color=ORANGE, lw=2)
    a2.set(ylabel="Fare per mile (USD)", title="Fare per mile falls with distance\n(fixed flag-drop is amortised)")
    save(fig, "05_trips_by_distance")

# --- 6. Top 10 routes --------------------------------------------------------
rows = sorted(read("routes"), key=lambda r: -int(r[1]))[:10]
if rows:
    lbl = []
    for r in rows:
        pu, do = r[0].split("->")
        lbl.append(f"{zones.get(int(pu),pu).split(' (')[0][:16]} -> {zones.get(int(do),do).split(' (')[0][:16]}")
    vals = [int(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(9.5, 4.5))
    ax.barh(lbl[::-1], vals[::-1], color=GREEN)
    ax.set(xlabel="Trips", title="Top 10 pickup -> drop-off routes by trip count")
    save(fig, "06_top10_routes")

# --- 7. Revenue versus distance ----------------------------------------------
rows = read("revenue")
if rows:
    pts = []
    for r in rows:
        try:
            pts.append((float(r[6]), float(r[4]), int(r[1])))   # avg_distance, revenue, trips
        except (ValueError, IndexError):
            pass
    if pts:
        x = [p[0] for p in pts]; y = [p[1] for p in pts]; s = [max(4, p[2] / 3000) for p in pts]
        fig, ax = plt.subplots(figsize=(8.5, 5))
        ax.scatter(x, y, s=s, alpha=.55, color=BLUE, edgecolors="none")
        ax.set(xlabel="Average trip distance from zone (miles)",
               ylabel="Total revenue generated by zone (USD)",
               title="Zone revenue vs average trip distance\n(bubble size = trip count)")
        ax.set_yscale("log")
        save(fig, "07_revenue_vs_distance")

print("\nAll figures written to", FIG)
