#!/usr/bin/env python3
"""
CIVIL DAWN AND SUNRISE FOR GOLDEN, BC, ON A FLAT HORIZON

    python civildawn.py

This answers a DIFFERENT question from goldensun.py, and the two must not be
conflated.

    goldensun.py  when does direct sunlight clear the MOUNTAIN RIDGE and reach
                  the townsite? Terrain included. Answers "is the sun on us".

    civildawn.py  when is there enough light outdoors to walk safely, on a
                  FLAT horizon? Terrain excluded. Answers "is it dark".

Civil dawn is the moment the sun's centre reaches 6 degrees below the horizon.
Before it, conditions outdoors are functionally dark. It is the standard
threshold for whether a person can see and be seen without artificial light,
which is why it, rather than sunrise, is the relevant measure for a child
walking to school.

Terrain is deliberately EXCLUDED here. Ridges block direct sun but they do not
stop the sky from lighting up, and civil dawn is about scattered light from the
whole sky rather than a beam from the sun. Including terrain would understate
available light.

WHY THIS FILE EXISTS
--------------------
The figures in council-briefing/golden-time-observance-source-sheet-2026-09-05.md
section 2 and section 3 were produced with the Python `astral` library, using a
script that is not in this repository. Those numbers were therefore not
reproducible from the published code, which is the single largest gap in the
package. This script recomputes them from solarpos.py, so everything in the
repository can be regenerated from the repository.

This is a RECOMPUTATION, not a verification. Three things differ from the
original astral run, so the numbers here may not match it exactly:

  1. Coordinates. The source sheet used 51.2967 N, 116.9631 W. This uses the
     project's coordinates, 51.2969 N, 116.9647 W, about 115 m away, so that
     the repository has one location rather than two.
  2. Sunrise convention. Handled: see UPPER_LIMB_DEG below.
  3. Refraction. solarpos applies refraction to the altitude before testing;
     astral's depression angles are geometric.

Where this disagrees with the source sheet, THIS is the reproducible number and
the source sheet is the one that needs correcting.
"""

import datetime as dt

import solarpos as sp
import goldensun as g

LAT, LON = g.LAT, g.LON

# The two clock options. Named for what they mean locally rather than by
# offset, because that is how the debate is actually conducted.
PACIFIC = g.MST          # UTC-7, BC's new permanent Pacific Time
PERMANENT_MDT = g.MDT    # UTC-6, the RDEK and Alberta choice

# Sunrise here uses the UPPER LIMB, the almanac convention, NOT the centre
# convention goldensun.py uses. That is deliberate: these figures are meant to
# be checkable against published sunrise tables, so they must use the same
# definition those tables use. selftest.py measures the gap between the two
# conventions at 1.2 to 2.4 minutes.
SUNRISE_ALTITUDE = sp.UPPER_LIMB_DEG
CIVIL_ALTITUDE = sp.CIVIL_TWILIGHT_DEG

# The winter the decision governs.
WINDOW_START = dt.date(2026, 10, 1)
WINDOW_END = dt.date(2027, 4, 30)

# ---------------------------------------------------------------------------
# School bell times
# ---------------------------------------------------------------------------
# Source:    the four schools' own websites, School District 6 Rocky Mountain.
# Retrieved: 2026-09-06.
#
#   Golden Secondary      gss.sd6.bc.ca/about-us/bell-schedule
#                         warning bell 8:40, Period 1 8:45-10:00
#   Alexander Park        apes.sd6.bc.ca/about-us/bell-schedule
#   Nicholson Elementary  TODO(Joy): URL not recorded, times supplied directly
#   Lady Grey Elementary  TODO(Joy): URL not recorded, times supplied directly
#
# These REPLACE the 8:20 and 8:30 figures used previously, which were inferred
# from bell times rather than sourced.
#
# IMPORTANT, and the reason these are not simply "the answer": a bell is an
# ARRIVAL time. Children are on the road BEFORE it, so a count anchored to a
# bell answers "was it dark when they arrived", not "was it dark while they
# walked", and therefore UNDERSTATES exposure. The sweep spans earlier times so
# the walking period stays visible. The two are different questions and this
# script reports them separately rather than merging them into one figure.
BELL_TIMES = [
    # school                  warning/welcoming  classes begin
    ("Nicholson Elementary",  dt.time(8, 40),    dt.time(8, 45)),
    ("Golden Secondary",      dt.time(8, 40),    dt.time(8, 45)),
    ("Alexander Park",        dt.time(8, 50),    dt.time(8, 55)),
    ("Lady Grey Elementary",  dt.time(8, 53),    dt.time(8, 58)),
]

# Reference lines in the sweep standing for students walking to reach the
# earliest 8:40 bell. INFERRED, not sourced, and labelled as such in output.
INFERRED_WALKING = (dt.time(8, 15), dt.time(8, 25))

SUNRISE_THRESHOLD = dt.time(8, 45)

# Because the walking window is inferred rather than measured, the headline
# count depends on a number nobody has sourced. Rather than pick one and hope,
# the sweep below reports the count at every five minutes across the plausible
# range, so a reader can see how fast the answer moves with the assumption.
SWEEP_START = dt.time(8, 0)
SWEEP_END = dt.time(8, 55)
SWEEP_STEP_MIN = 5

# Reference rows from the US Naval Observatory, same query as selftest.py.
# URL:       https://aa.usno.navy.mil/api/rstt/oneday
#                ?date=YYYY-MM-DD&coords=51.2969,-116.9647&tz=-7
# Retrieved: 2026-09-06, tz UTC-7 no DST, flat horizon.
USNO_CHECK = [
    # date          civil_begin  sunrise
    ("2026-12-21",  "08:10",     "08:50"),
    ("2027-01-15",  "08:08",     "08:46"),
    ("2027-03-20",  "06:17",     "06:51"),
    ("2027-06-21",  "03:44",     "04:32"),
]


def dawn_and_sunrise(date, tz):
    """(civil dawn, sunrise) as local clock times, or (None, None)."""
    dawn, _ = sp.crossings(date, tz, LAT, LON, CIVIL_ALTITUDE)
    rise, _ = sp.crossings(date, tz, LAT, LON, SUNRISE_ALTITUDE)
    return dawn, rise


def hhmm(when):
    return "  --  " if when is None else when.strftime("%H:%M")


def verify_against_usno():
    """Independent check, since these figures carry the political weight."""
    print("=" * 74)
    print("CHECK  against US Naval Observatory (retrieved 2026-09-06, UTC-7)")
    print("=" * 74)
    worst = 0.0
    for iso, cb, sr in USNO_CHECK:
        date = dt.date.fromisoformat(iso)
        dawn, rise = dawn_and_sunrise(date, -7)
        for label, got, want in (("civil dawn", dawn, cb), ("sunrise", rise, sr)):
            ref = dt.datetime.combine(date, dt.time(int(want[:2]), int(want[3:])))
            delta = (got - ref).total_seconds() / 60.0
            worst = max(worst, abs(delta))
            print(f"  {iso}  {label:11s} {got.strftime('%H:%M:%S')}  "
                  f"vs {want}   {delta:+5.2f} min")
    print(f"\n  Worst deviation {worst:.2f} min. Using the upper-limb sunrise")
    print("  convention, these should agree closely; a large gap would mean the")
    print("  recomputation is not comparable to published tables.\n")
    return worst


def table():
    """Section 2 of the source sheet, recomputed."""
    print("=" * 74)
    print("CIVIL DAWN AND SUNRISE, GOLDEN BC (flat horizon, no terrain)")
    print("=" * 74)
    print(f"  {'':<14} | {'BC PACIFIC (UTC-7)':^23} | "
          f"{'PERMANENT MDT (UTC-6)':^23}")
    print(f"  {'date':<14} | {'civil dawn':>11} {'sunrise':>11} | "
          f"{'civil dawn':>11} {'sunrise':>11}")
    print("  " + "-" * 70)
    dates = [dt.date(2026, 11, 2), dt.date(2026, 11, 15), dt.date(2026, 12, 1),
             dt.date(2026, 12, 15), dt.date(2026, 12, 21), dt.date(2027, 1, 5),
             dt.date(2027, 1, 15), dt.date(2027, 2, 1), dt.date(2027, 3, 1)]
    for date in dates:
        pd, pr = dawn_and_sunrise(date, PACIFIC)
        md, mr = dawn_and_sunrise(date, PERMANENT_MDT)
        print(f"  {date.strftime('%d %b %Y'):<14} | {hhmm(pd):>11} {hhmm(pr):>11} | "
              f"{hhmm(md):>11} {hhmm(mr):>11}")
    print()


def verify_clock_offset():
    """The two options describe the SAME instant with two different clocks.

    So every time under permanent MDT must read exactly 60 minutes later than
    under Pacific. Anything else is a timezone-handling bug, not a result.
    This is also what licenses counts() to compute each day once and shift,
    rather than doing the solar arithmetic twice.
    """
    print("=" * 74)
    print("CHECK  permanent MDT reads exactly 60 minutes later than Pacific")
    print("=" * 74)
    STEP_DAYS = 7                       # weekly sample, for speed
    worst, failures, tested, days = 0.0, 0, 0, 0
    total_days = (WINDOW_END - WINDOW_START).days + 1
    day = WINDOW_START
    while day <= WINDOW_END:
        days += 1
        pd, pr = dawn_and_sunrise(day, PACIFIC)
        md, mr = dawn_and_sunrise(day, PERMANENT_MDT)
        for a, b in ((pd, md), (pr, mr)):
            if a is None or b is None:
                continue
            tested += 1
            gap = (b - a).total_seconds() / 60.0
            worst = max(worst, abs(gap - 60.0))
            if abs(gap - 60.0) > 1e-6:
                failures += 1
        day += dt.timedelta(days=STEP_DAYS)
    status = "PASS" if failures == 0 else f"FAIL ({failures} rows)"
    print(f"  Sampled every {STEP_DAYS} days: {days} of {total_days} days, "
          f"{tested} time pairs tested.")
    print(f"  This is a SAMPLE, not the whole window.")
    print(f"  Worst deviation from exactly 60 min: {worst:.9f}   {status}\n")
    return failures == 0


def counts():
    """Section 3 of the source sheet, recomputed."""
    print("=" * 74)
    print(f"COUNTS, {WINDOW_START.isoformat()} to {WINDOW_END.isoformat()}")
    print("=" * 74)

    thresholds = sorted({b for _, b, _ in BELL_TIMES}
                        | {c for _, _, c in BELL_TIMES})
    dark = {t: {PACIFIC: [], PERMANENT_MDT: []} for t in thresholds}
    late_sunrise = {PACIFIC: [], PERMANENT_MDT: []}
    hour = dt.timedelta(hours=1)

    day = WINDOW_START
    while day <= WINDOW_END:
        # Compute once under Pacific, then shift. Verified equivalent to
        # computing both by verify_clock_offset above.
        dawn, rise = dawn_and_sunrise(day, PACIFIC)
        for tz, shift in ((PACIFIC, dt.timedelta(0)), (PERMANENT_MDT, hour)):
            for threshold in thresholds:
                if dawn is not None and (dawn + shift).time() > threshold:
                    dark[threshold][tz].append(day)
            if rise is not None and (rise + shift).time() > SUNRISE_THRESHOLD:
                late_sunrise[tz].append(day)
        day += dt.timedelta(days=1)

    total = (WINDOW_END - WINDOW_START).days + 1
    print(f"  {total} days in the window.")
    print("  A bell is an ARRIVAL time. These count mornings still fully dark")
    print("  AT the bell, so they understate the walk that precedes it.\n")

    def span(days):
        if not days:
            return ""
        return f"  ({days[0].strftime('%b %d')} to {days[-1].strftime('%b %d')})"

    print(f"  {'school':<22} {'bell':>6} {'Pacific':>8} {'perm MDT':>9}")
    print("  " + "-" * 62)
    for school, warning, classes in BELL_TIMES:
        for label, t in ((f"{school}", warning), ("    classes begin", classes)):
            p, m = dark[t][PACIFIC], dark[t][PERMANENT_MDT]
            print(f"  {label:<22} {t.strftime('%H:%M'):>6} {len(p):>8} "
                  f"{len(m):>9}{span(m)}")
    print()
    label = SUNRISE_THRESHOLD.strftime("%H:%M")
    p, m = late_sunrise[PACIFIC], late_sunrise[PERMANENT_MDT]
    print(f"  Days sunrise falls after {label}")
    print(f"      BC Pacific      {len(p):3d}{span(p)}")
    print(f"      Permanent MDT   {len(m):3d}{span(m)}")
    print()


def threshold_sweep():
    """How much does the headline count depend on the assumed walking time?"""
    print("=" * 74)
    print("THRESHOLD SENSITIVITY")
    print("=" * 74)
    print("  Days still fully dark (before civil dawn) at each clock time,")
    print(f"  {WINDOW_START.isoformat()} to {WINDOW_END.isoformat()}.")
    print("  Bell times are sourced. WALKING times are not: nobody has measured")
    print("  when Golden children actually leave home, so the whole range is")
    print("  shown rather than one chosen value. The bell rows answer 'dark on")
    print("  arrival'; the earlier rows answer 'dark while walking'.\n")
    print(f"  {'time':>7} | {'BC Pacific':>12} | {'Permanent MDT':>14} | "
          f"{'difference':>11}")
    print("  " + "-" * 54)

    # Compute each day's civil dawn once, then test it against every threshold.
    dawns = []
    day = WINDOW_START
    while day <= WINDOW_END:
        dawn, _ = dawn_and_sunrise(day, PACIFIC)
        if dawn is not None:
            dawns.append(dawn)
        day += dt.timedelta(days=1)

    # Label rows that correspond to something real, so a reader can tell a
    # sourced bell from a round number on the grid.
    notes = {}
    short = {"Nicholson Elementary": "Nicholson", "Golden Secondary": "GSS",
             "Alexander Park": "Alexander Park", "Lady Grey Elementary": "Lady Grey"}
    for school, warning, classes in BELL_TIMES:
        notes.setdefault(warning, []).append(short[school] + " bell")
        notes.setdefault(classes, []).append(short[school] + " classes")
    for t in INFERRED_WALKING:
        notes.setdefault(t, []).append("inferred walking time")

    hour = dt.timedelta(hours=1)
    grid = set(range(SWEEP_START.hour * 60 + SWEEP_START.minute,
                     SWEEP_END.hour * 60 + SWEEP_END.minute + 1,
                     SWEEP_STEP_MIN))
    grid |= {t.hour * 60 + t.minute for t in notes}

    for minutes in sorted(grid):
        threshold = dt.time(minutes // 60, minutes % 60)
        p = sum(1 for d in dawns if d.time() > threshold)
        m = sum(1 for d in dawns if (d + hour).time() > threshold)
        note = ", ".join(notes.get(threshold, []))
        print(f"  {threshold.strftime('%H:%M'):>7} | {p:>12} | {m:>14} | "
              f"{m - p:>11}   {note}")
    print()
    print("  Rows without a note are grid points, not sourced times.")
    print()


def main():
    verify_against_usno()
    verify_clock_offset()
    table()
    counts()
    threshold_sweep()
    print("=" * 74)
    print("These are FLAT-HORIZON figures about whether it is light enough to")
    print("be outdoors. They are not the terrain figures from goldensun.py,")
    print("which are about direct sun reaching the town. Do not mix them.")
    print("=" * 74)


if __name__ == "__main__":
    main()
