"""
TRUE SUN-ON-TOWN TIMES FOR GOLDEN, BC
Permanent Mountain Standard Time (UTC-7) vs permanent Mountain Daylight Time (UTC-6)

Almanac sunrise assumes you are standing on a featureless plain. Golden is not
on a plain. This script works out when the sun actually clears the ridge as
seen from the townsite, and when it drops behind the other side.

    python goldensun.py                 # real terrain (downloads ~75 MB of DEM once)
    python goldensun.py --flat          # self-test: pretend the world is flat

The --flat run is a check on the machinery. With a flat horizon the answers
must reproduce standard almanac sunrise and sunset. If they do, the pipeline
is sound and any difference in the real run is terrain, not a bug.
"""

import argparse
import datetime as dt

import numpy as np

from solarpos import sun_position, solar_declination
import horizon as hz

# Townsite: Golden civic centre area, 51 deg 17'49" N, 116 deg 57'53" W
LAT, LON = 51.2969, -116.9647

# The two clock options, as offsets from UTC. Everything is reported for both.
MST, MDT = -7, -6

# Morning clock times the annual day-counts are measured against. All three are
# reported; pick the one that matches your school's bell times.
MORNING_THRESHOLDS = (8, 9, 10)

# The year everything is calculated for. This is the ONLY place a year is set;
# diagnostics.py and season.py both import it rather than repeating it. It
# defaults to the next full calendar year so that it does not silently go stale,
# and every script prints the year it used so no one misreads an old table.
ANALYSIS_YEAR = dt.date.today().year + 1


# ---------------------------------------------------------------------------
# Astronomical dates, derived rather than typed in
# ---------------------------------------------------------------------------
# Solstices and equinoxes drift by a day between years, so hardcoding them
# means a second thing to keep in step with the year. Instead we find them from
# the sun's declination: how far north or south of the equator it stands. That
# reaches its minimum at the December solstice, its maximum in June, and passes
# through zero at the equinoxes.

def _best_day(first, last, score):
    """The date in [first, last] with the lowest `score(declination)`.

    Declination is sampled at 19:00 UTC, which is midday at Golden, so the date
    returned is the one somebody standing in Golden would call the solstice.
    """
    best, best_score = None, None
    day = first
    while day <= last:
        value = score(solar_declination(dt.datetime.combine(day, dt.time(19, 0))))
        if best_score is None or value < best_score:
            best, best_score = day, value
        day += dt.timedelta(days=1)
    return best


def december_solstice(year):
    """Shortest day. Declination is at its most negative."""
    return _best_day(dt.date(year, 12, 17), dt.date(year, 12, 26), lambda d: d)


def june_solstice(year):
    """Longest day. Declination is at its most positive."""
    return _best_day(dt.date(year, 6, 17), dt.date(year, 6, 26), lambda d: -d)


def march_equinox(year):
    """Declination closest to zero in March."""
    return _best_day(dt.date(year, 3, 16), dt.date(year, 3, 25), abs)


def september_equinox(year):
    """Declination closest to zero in September."""
    return _best_day(dt.date(year, 9, 17), dt.date(year, 9, 26), abs)


def seasonal_dates(year):
    """The seven sample dates. The December solstice is the one that OPENS the
    winter being studied, so it falls in the previous calendar year."""
    return [
        ("Winter solstice", december_solstice(year - 1)),
        ("Jan 15",          dt.date(year,  1, 15)),
        ("Feb 1",           dt.date(year,  2,  1)),
        ("Spring equinox",  march_equinox(year)),
        ("Summer solstice", june_solstice(year)),
        ("Fall equinox",    september_equinox(year)),
        ("Nov 15",          dt.date(year, 11, 15)),
    ]


def sun_events(date, tz_offset, azimuths, angles, step_minutes=1):
    """First and last local clock time the sun is above the real skyline."""
    visible = []
    t = dt.datetime.combine(date, dt.time(0, 0)) - dt.timedelta(hours=tz_offset)
    for _ in range(24 * 60 // step_minutes):
        alt, az = sun_position(t, LAT, LON)
        if alt > hz.angle_at(azimuths, angles, az):
            visible.append(t + dt.timedelta(hours=tz_offset))
        t += dt.timedelta(minutes=step_minutes)
    if not visible:
        return None, None, 0.0
    hours = len(visible) * step_minutes / 60.0
    return visible[0], visible[-1], hours


def clock(x):
    return "  --  " if x is None else x.strftime("%H:%M")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true",
                    help="self-test with a zero horizon instead of real terrain")
    ap.add_argument("--radius", type=float, default=60.0, help="look-out distance, km")
    ap.add_argument("--year", type=int, default=ANALYSIS_YEAR,
                    help=f"calendar year to report (default {ANALYSIS_YEAR})")
    args = ap.parse_args()

    dates = seasonal_dates(args.year)
    print(f"Reporting for calendar year {args.year}. "
          f"Winter solstice used: {dates[0][1].isoformat()}.\n")

    if args.flat:
        print("SELF-TEST: flat horizon (0 deg in every direction)\n")
        azimuths = np.arange(0.0, 360.0, 0.5)
        angles = np.zeros_like(azimuths)
    else:
        print(f"Loading elevation data within {args.radius:.0f} km of the townsite...")
        grid, lat0, lon0, step = hz.load_mosaic(LAT, LON, args.radius)
        print(f"  grid {grid.shape[0]} x {grid.shape[1]} points, "
              f"{step*3600:.0f} arc-second spacing")
        print("Tracing the skyline on 720 compass bearings...")
        azimuths, angles = hz.horizon_profile(grid, lat0, lon0, step, LAT, LON,
                                              radius_km=args.radius)
        print(f"  highest ridge {angles.max():.1f} deg at bearing "
              f"{azimuths[angles.argmax()]:.0f} deg\n")

        print("  Skyline by direction (degrees above level):")
        for name, az in [("N", 0), ("NE", 45), ("E", 90), ("SE", 135),
                         ("S", 180), ("SW", 225), ("W", 270), ("NW", 315)]:
            print(f"    {name:<3} {hz.angle_at(azimuths, angles, az):5.1f}")
        print()

    hdr = f"{'':<16} | {'MST (UTC-7)':^26} | {'MDT (UTC-6)':^26}"
    print(hdr)
    print(f"{'':<16} | {'sun on':>8} {'sun off':>8} {'hrs':>7} | "
          f"{'sun on':>8} {'sun off':>8} {'hrs':>7}")
    print("-" * len(hdr))

    for label, date in dates:
        r7, s7, h7 = sun_events(date, MST, azimuths, angles)
        r6, s6, h6 = sun_events(date, MDT, azimuths, angles)
        print(f"{label:<16} | {clock(r7):>8} {clock(s7):>8} {h7:7.2f} | "
              f"{clock(r6):>8} {clock(s6):>8} {h6:7.2f}")

    if args.flat:
        # The table above is only meaningful if somebody compares it against
        # published values. Rather than leave that to the reader, run the
        # checks and say PASS or FAIL outright.
        print()
        import selftest
        return 0 if selftest.run_all(args.year) else 1

    # How many days a year does the sun reach the town after 8, 9 and 10am?
    print(f"\nDays in {args.year} the sun clears the ridge after a given clock time:")
    for threshold in MORNING_THRESHOLDS:
        counts = {}
        for tz in (MST, MDT):
            n = 0
            d = dt.date(args.year, 1, 1)
            while d.year == args.year:
                on, _, _ = sun_events(d, tz, azimuths, angles, step_minutes=2)
                if on is not None and on.hour + on.minute / 60 > threshold:
                    n += 1
                d += dt.timedelta(days=1)
            counts[tz] = n
        print(f"  after {threshold:2d}:00   MST: {counts[MST]:3d}    MDT: {counts[MDT]:3d}")


if __name__ == "__main__":
    raise SystemExit(main())
