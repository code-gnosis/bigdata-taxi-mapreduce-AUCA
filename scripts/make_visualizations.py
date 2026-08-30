#!/usr/bin/env python3
"""
SECTION 14 -- REQUIRED VISUALIZATIONS

Renders the seven required charts from the MapReduce results in output/local/.

Sized for a portrait A4/Letter page with 2.4 cm margins (usable width ~16 cm / 6.3 in).
Figures are drawn 7 in wide at 200 dpi so they stay crisp when the word processor
scales them down to the text column.

NOTE ON A BUG THIS VERSION FIXES: passing duplicate label strings to barh() makes
matplotlib treat them as one category and silently merge the bars. Truncating zone
names collapsed "Upper East Side South" and "Upper East Side North" into the same
label, so a "top 10" chart drew only 6 bars. All categorical charts below therefore
plot against explicit integer positions and set the tick labels separately.
"""
import os
import csv
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.expanduser("~/taxi_project")
LOCAL = f"{BASE}/output/local"
FIG = f"{BASE}/report/figures"
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "font.size": 9,
    "axes.grid": True,
    "grid.alpha": .25,
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
BLUE, GREEN, ORANGE, GREY = "#2b6cb0", "#2f855a", "#c05621", "#a0aec0"
W = 7.0                      # inches - fits the text column of a portrait page

zones = {}
with open(f"{BASE}/data/taxi_zone_lookup.csv") as fh:
    for r in csv.DictReader(fh):
        zones[int(r["LocationID"])] = (r["Zone"], r["Borough"])

def zname(i, with_borough=True):
    z = zones.get(int(i))
    if not z:
        return f"Zone {int(i)}"
    return f"{z[0]} ({z[1]})" if with_borough else z[0]

def read(name):
    p = f"{LOCAL}/{name}.tsv"
    if not os.path.exists(p):
        print(f"  !! missing {p}")
        return []
    with open(p) as fh:
        return [ln.rstrip("\n").split("\t") for ln in fh if ln.strip()]

def save(fig, name):
    fig.savefig(f"{FIG}/{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {name}.png")

def hbar(ax, labels, values, colour):
    """Horizontal bars against explicit positions -- never merges duplicate labels."""
    pos = range(len(labels))
    ax.barh(list(pos), values, color=colour, height=.72)
    ax.set_yticks(list(pos))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()                      # rank 1 at the top
    ax.margins(x=.12)                      # headroom so value labels fit
    for p, v in zip(pos, values):
        ax.text(v, p, f"  {v:,.0f}", va="center", ha="left", fontsize=7.5)

# ---------------------------------------------------------------- 1. by hour
rows = sorted(read("hourly"), key=lambda r: r[0])
if rows:
    hrs = [int(r[0]) for r in rows]
    trips = [int(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(W, 3.2))
    bars = ax.bar(hrs, trips, color=BLUE, width=.75)
    hi, lo = trips.index(max(trips)), trips.index(min(trips))
    bars[hi].set_color(ORANGE)
    bars[lo].set_color(GREY)
    ax.set_ylim(0, max(trips) * 1.16)
    ax.set(xlabel="Hour of day", ylabel="Trips",
           title="Figure 1  Taxi demand by hour of day (Jan-Mar 2024)")
    ax.set_xticks(range(24))
    ax.tick_params(axis="x", labelsize=7.5)
    ax.annotate(f"busiest {hrs[hi]:02d}:00\n{trips[hi]:,}", (hrs[hi], trips[hi]),
                textcoords="offset points", xytext=(0, 7), ha="center",
                fontsize=7.5, color=ORANGE, fontweight="bold")
    ax.annotate(f"quietest {hrs[lo]:02d}:00\n{trips[lo]:,}", (hrs[lo], trips[lo]),
                textcoords="offset points", xytext=(0, 7), ha="center",
                fontsize=7.5, color="#4a5568")
    save(fig, "01_trips_by_hour")

# ---------------------------------------------------------------- 2. by day
rows = sorted([r for r in read("daily") if not r[0].startswith("SUMMARY")],
              key=lambda r: r[0])
if rows:
    names = [r[0].split("_", 1)[1] for r in rows]
    trips = [int(r[1]) for r in rows]
    cols = [ORANGE if r[4] == "WEEKEND" else BLUE for r in rows]
    fig, ax = plt.subplots(figsize=(W, 3.0))
    ax.bar(range(len(names)), trips, color=cols, width=.7)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylim(0, max(trips) * 1.14)
    ax.set(ylabel="Trips", title="Figure 2  Demand by day of week (orange = weekend)")
    for i, v in enumerate(trips):
        ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=7.5)
    save(fig, "02_trips_by_day")

# ---------------------------------------------------------------- 3. top zones
rows = sorted(read("locations"), key=lambda r: -int(r[1]))[:10]
if rows:
    labels = [zname(r[0]) for r in rows]          # full names, no truncation
    vals = [int(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(W, 3.6))
    hbar(ax, labels, vals, BLUE)
    ax.set(xlabel="Trips", title="Figure 3  Top 10 pickup zones by trip count")
    save(fig, "03_top10_pickup_zones")

# ---------------------------------------------------------------- 4. payment
rows = sorted(read("payment"), key=lambda r: -float(r[2]))
if rows:
    labels = [r[0].split("_", 1)[1] for r in rows]
    rev = [float(r[2]) for r in rows]
    tip = [float(r[5]) for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 3.0))
    a1.bar(range(len(labels)), rev, color=GREEN, width=.65)
    a1.set_xticks(range(len(labels)))
    a1.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    a1.set(ylabel="Total revenue (USD)", title="Revenue by payment method")
    a2.bar(range(len(labels)), tip, color=ORANGE, width=.65)
    a2.set_xticks(range(len(labels)))
    a2.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    a2.set(ylabel="Tip as % of fare", title="Tip rate (cash tips are not metered)")
    for i, v in enumerate(tip):
        a2.text(i, v, f"{v:.1f}%", ha="center", va="bottom", fontsize=7.5)
    fig.suptitle("Figure 4  Payment method: revenue and tipping", fontsize=9.5, y=1.03)
    save(fig, "04_revenue_by_payment")

# ---------------------------------------------------------------- 5. distance
rows = sorted(read("distance"), key=lambda r: r[0])
if rows:
    labels = [r[0].split("_", 1)[1] for r in rows]
    trips = [int(r[1]) for r in rows]
    fpm = [float(r[6]) for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 3.0))
    a1.bar(range(len(labels)), trips, color=BLUE, width=.65)
    a1.set_xticks(range(len(labels))); a1.set_xticklabels(labels, fontsize=8)
    a1.set(ylabel="Trips", title="Trips by distance band")
    a2.plot(range(len(labels)), fpm, "o-", color=ORANGE, lw=2)
    a2.set_xticks(range(len(labels))); a2.set_xticklabels(labels, fontsize=8)
    a2.set(ylabel="Fare per mile (USD)", title="Fare per mile falls with distance")
    for i, v in enumerate(fpm):
        a2.annotate(f"${v:.2f}", (i, v), textcoords="offset points",
                    xytext=(0, 7), ha="center", fontsize=7.5)
    a2.set_ylim(0, max(fpm) * 1.25)
    fig.suptitle("Figure 5  Distance bands: volume and unit economics", fontsize=9.5, y=1.03)
    save(fig, "05_trips_by_distance")

# ---------------------------------------------------------------- 6. routes
rows = sorted(read("routes"), key=lambda r: -int(r[1]))[:10]
if rows:
    labels = []
    for r in rows:
        pu, do = r[0].split("->")
        # full zone names, wrapped -- NOT truncated, or duplicates merge
        labels.append(textwrap.fill(f"{zname(pu, False)} → {zname(do, False)}", 34))
    vals = [int(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(W, 4.4))
    hbar(ax, labels, vals, GREEN)
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set(xlabel="Trips", title="Figure 6  Top 10 routes by trip count")
    save(fig, "06_top10_routes")

# ---------------------------------------------------------------- 7. rev vs dist
rows = read("revenue")
if rows:
    pts = []
    for r in rows:
        try:
            pts.append((float(r[6]), float(r[4]), int(r[1]), int(r[0])))
        except (ValueError, IndexError):
            pass
    if pts:
        x = [p[0] for p in pts]; y = [p[1] for p in pts]
        s = [max(5, p[2] / 2500) for p in pts]
        fig, ax = plt.subplots(figsize=(W, 4.0))
        ax.scatter(x, y, s=s, alpha=.5, color=BLUE, edgecolors="none")
        # label the four highest-revenue zones
        for p in sorted(pts, key=lambda t: -t[1])[:4]:
            ax.annotate(zname(p[3], False), (p[0], p[1]), textcoords="offset points",
                        xytext=(7, 4), fontsize=7.5, color="#2d3748")
        ax.set_yscale("log")
        ax.set(xlabel="Average trip distance from zone (miles)",
               ylabel="Total revenue by zone, USD (log scale)",
               title="Figure 7  Zone revenue vs average trip distance (bubble = trip count)")
        save(fig, "07_revenue_vs_distance")

print("\nFigures written to", FIG)
