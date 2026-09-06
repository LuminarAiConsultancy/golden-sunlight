#!/usr/bin/env python3
"""
SUMMER (or any month) FROM THE SAVED SKYLINE

Reads skyline_full.csv, written by diagnostics.py, so it needs no elevation
tiles and runs in seconds.

    C:\\Python314\\python.exe season.py              # July and August
    C:\\Python314\\python.exe season.py 5 6 7 8 9    # any months you like
"""

import datetime as dt
import sys

import numpy as np

import goldensun as g
from solarpos import sun_position

LAT, LON = g.LAT, g.LON
YEAR = 2027

az_grid, horizon = np.loadtxt("skyline_full.csv", delimiter=",",
                              skiprows=1, unpack=True)


def day(date, tz):
    """Sun-on, sun-off and total direct sun for one date, in decimal hours."""
    vis = []
    t = dt.datetime.combine(date, dt.time(0, 0)) - dt.timedelta(hours=tz)
    for _ in range(24 * 60):
        alt, az = sun_position(t, LAT, LON)
        if alt > np.interp(az % 360, az_grid, horizon, period=360.0):
            loc = t + dt.timedelta(hours=tz)
            vis.append(loc.hour + loc.minute / 60)
        t += dt.timedelta(minutes=1)
    if not vis:
        return None, None, 0.0
    return vis[0], vis[-1], len(vis) / 60


def hm(h):
    if h is None:
        return "  --  "
    m = int(round(h * 60))
    hr, mi = m // 60, m % 60
    return f"{hr%12 or 12}:{mi:02d} {'am' if hr<12 else 'pm'}"


months = [int(a) for a in sys.argv[1:]] or [7, 8]
NAMES = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
         6: "June", 7: "July", 8: "August", 9: "September", 10: "October",
         11: "November", 12: "December"}

for mo in months:
    d = dt.date(YEAR, mo, 1)
    rows, evening7, evening8 = [], {-7: 0, -6: 0}, {-7: 0, -6: 0}
    print()
    print("=" * 74)
    print(f"{NAMES[mo]} {YEAR}   (terrain included)")
    print("=" * 74)
    print(f"  {'date':>6} | {'STANDARD sun on / off':^26} | "
          f"{'DAYLIGHT sun on / off':^26}")
    while d.month == mo:
        a_on, a_off, a_h = day(d, -7)
        b_on, b_off, b_h = day(d, -6)
        rows.append((a_h, b_h))
        for tz, off in ((-7, a_off), (-6, b_off)):
            if off and off >= 19:
                evening7[tz] += 1
            if off and off >= 20:
                evening8[tz] += 1
        if d.day % 5 == 1 or d.day == 1:
            print(f"  {d.strftime('%d %b'):>6} | {hm(a_on):>11} to {hm(a_off):<11} | "
                  f"{hm(b_on):>11} to {hm(b_off):<11}")
        d += dt.timedelta(days=1)

    n = len(rows)
    print(f"\n  Direct sun averages {np.mean([r[0] for r in rows]):.2f} h/day, "
          f"identical under both clocks.")
    print(f"  Days with sun still on the town at 7 pm:  "
          f"standard {evening7[-7]:2d} of {n}    daylight {evening7[-6]:2d} of {n}")
    print(f"  Days with sun still on the town at 8 pm:  "
          f"standard {evening8[-7]:2d} of {n}    daylight {evening8[-6]:2d} of {n}")

print()
print("Note: this is DIRECT sun on the townsite. Usable light lasts roughly")
print("40 to 50 minutes past that in midsummer at this latitude, because")
print("twilight is long even once the sun is behind the ridge.")
