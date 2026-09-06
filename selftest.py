#!/usr/bin/env python3
"""
SELF-TEST for the solar half of this project.

Run it directly, or as part of `python goldensun.py --flat`:

    python selftest.py

Two independent kinds of check.

PART A compares flat-horizon sunrise, sunset and solar noon against published
values from an outside authority. This is the check that would catch a wrong
constant or a sign error.

PART B checks internal invariants that must hold whatever the reference says:
the sun's declination cannot exceed the tilt of the Earth's axis, it must be
near zero at an equinox, and on a flat horizon sunrise and sunset must be
symmetric about solar noon. These need no network and no external source, and
they catch gross errors on their own.

WHAT THIS DOES AND DOES NOT PROVE
---------------------------------
solarpos.py implements the NOAA Solar Calculator algorithm. The reference below
is the US Naval Observatory, which is a separate implementation by a separate
institution, but both descend from the same body of standard astronomical
theory. So agreement here demonstrates that THIS CODE IMPLEMENTS THE ALGORITHM
CORRECTLY. It is not an independent confirmation that the underlying algorithm
is right, and it should not be described as one. Checking NOAA-derived code
against a NOAA-derived calculator would be more circular still, which is why
the reference is USNO rather than NOAA's own web calculator.

The terrain half of the project is NOT tested here. It cannot be checked
without the elevation tiles, and no published skyline profile for Golden exists
to check it against.
"""

import datetime as dt

import solarpos as sp
from solarpos import solar_declination
import goldensun as g

LAT, LON = g.LAT, g.LON

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
# Source:     US Naval Observatory, Astronomical Applications Department.
#             Rise/Set/Transit/Twilight Data, one-day JSON API.
# URL format: https://aa.usno.navy.mil/api/rstt/oneday
#                 ?date=YYYY-MM-DD&coords=51.2969,-116.9647&tz=-7
# Coordinates queried: 51.2969 N, 116.9647 W. These are the same coordinates
#             the model uses (goldensun.LAT / goldensun.LON).
# Time zone:  UTC-7, no daylight saving, matching permanent Mountain Standard.
# Horizon:    flat / sea-level. USNO assumes an unobstructed horizon, which is
#             why this can only ever test the --flat path, never the terrain.
# Retrieved:  2026-09-06.
#
# Times are local clock (UTC-7), 24-hour.
USNO = [
    # date          civil_begin  rise     transit  set      civil_end
    ("2026-12-21",  "08:10",     "08:50", "12:46", "16:42", "17:22"),
    ("2027-01-15",  "08:08",     "08:46", "12:57", "17:09", "17:47"),
    ("2027-03-20",  "06:17",     "06:51", "12:55", "19:01", "19:34"),
    ("2027-06-21",  "03:44",     "04:32", "12:50", "21:08", "21:55"),
]
REFERENCE_TZ = -7

# Tolerance, and where it comes from. This is NOT tuned to make rows pass.
#
#   3 minutes  documented centre-versus-upper-limb convention gap, recorded in
#              golden-daylight-method-2026-09-04.md as "two to three minutes"
# + 1 minute   the sampling granularity used elsewhere in the project
# = 4 minutes
#
# USNO marks sunrise when the sun's UPPER LIMB reaches the horizon; this code
# finds when the refracted CENTRE crosses zero. The centre is roughly one solar
# semidiameter lower at that moment, so our sunrise must land slightly LATER
# than USNO's and our sunset slightly EARLIER, by a similar amount on every
# row. That systematic, one-signed pattern is itself part of the test: see
# check_convention_signature below. Deviations scattered in sign or size would
# indicate a real defect that a pass at 4 minutes would hide.
TOLERANCE_MIN = 4.0

# Civil twilight is reported separately from sunrise and sunset because there
# is no limb convention involved: both USNO and this code mark it by the sun's
# CENTRE reaching -6 degrees, so the systematic offset seen in the rise/set
# rows should not appear here, and mixing them would blur two effects.
#
# This tolerance was originally set to 8 minutes on the argument that USNO's
# -6 degrees is geometric while sun_position applies refraction first, which
# would displace the two definitions. Measured deviations are all under one
# minute, so that argument is not supported and the extra slack had nothing
# behind it. Set to the same 4 minutes as rise and set. Recorded rather than
# quietly changed, because a tolerance nobody can justify is not a test.
CIVIL_ALTITUDE = -6.0
CIVIL_TOLERANCE_MIN = 4.0


# ---------------------------------------------------------------------------
# Machinery
# ---------------------------------------------------------------------------

def crossings(date, tz, target=0.0):
    """Thin wrapper over solarpos.crossings for this project's location."""
    return sp.crossings(date, tz, LAT, LON, target)


def transit(date, tz):
    """Thin wrapper over solarpos.transit for this project's location."""
    return sp.transit(date, tz, LAT, LON)


def _delta_minutes(computed, published, date):
    """Signed minutes: positive means this code is LATER than the reference."""
    ref = dt.datetime.combine(date, dt.time(int(published[:2]), int(published[3:])))
    return (computed - ref).total_seconds() / 60.0


def _row(label, computed, published, date, tolerance, failures):
    # The summary at the end has to be readable on its own, so failures are
    # recorded with their date rather than as a bare "sunrise" four times over.
    key = f"{label} on {date.isoformat()}"
    if computed is None:
        print(f"  {label:28s} {'--':>8}  vs {published}   FAIL (no crossing)")
        failures.append(key)
        return None
    d = _delta_minutes(computed, published, date)
    ok = abs(d) <= tolerance
    if not ok:
        failures.append(f"{key} (off by {d:+.2f} min)")
    print(f"  {label:28s} {computed.strftime('%H:%M:%S'):>8}  vs {published}"
          f"   {d:+6.2f} min   {'PASS' if ok else 'FAIL'}")
    return d


# ---------------------------------------------------------------------------
# PART A: against published values
# ---------------------------------------------------------------------------

def check_against_usno():
    print("=" * 78)
    print("PART A  Flat horizon vs US Naval Observatory (retrieved 2026-09-06)")
    print("=" * 78)
    print(f"  Location 51.2969 N, 116.9647 W, times in UTC{REFERENCE_TZ}, "
          f"tolerance {TOLERANCE_MIN:.0f} min")
    print(f"  Delta is this code minus USNO. Positive means later.\n")

    failures, rise_d, set_d = [], [], []

    for iso, _cb, rise, tran, sset, _ce in USNO:
        date = dt.date.fromisoformat(iso)
        up, down = crossings(date, REFERENCE_TZ)
        print(f"  {iso}")
        d1 = _row("sunrise", up, rise, date, TOLERANCE_MIN, failures)
        d2 = _row("transit (solar noon)", transit(date, REFERENCE_TZ), tran,
                  date, TOLERANCE_MIN, failures)
        d3 = _row("sunset", down, sset, date, TOLERANCE_MIN, failures)
        if d1 is not None:
            rise_d.append(d1)
        if d3 is not None:
            set_d.append(d3)
        print()

    return failures, rise_d, set_d


def check_convention_signature(rise_d, set_d, failures):
    """The deviations must be systematic, not scattered.

    Because USNO uses the upper limb and this code uses the centre, every
    sunrise must come out LATE and every sunset EARLY. A mixed set of signs
    means something other than the convention is moving the times, and that
    would be a defect hiding behind a passing tolerance.
    """
    print("=" * 78)
    print("PART A2  Is the deviation systematic, as the convention predicts?")
    print("=" * 78)

    checks = [
        ("every sunrise later than USNO", all(d > 0 for d in rise_d)),
        ("every sunset earlier than USNO", all(d < 0 for d in set_d)),
    ]
    if rise_d and set_d:
        spread = max(max(rise_d) - min(rise_d), max(set_d) - min(set_d))
        checks.append((f"deviation spread under 2 min ({spread:.2f})", spread < 2.0))

    for label, ok in checks:
        print(f"  {label:52s} {'PASS' if ok else 'FAIL'}")
        if not ok:
            failures.append(label)

    if rise_d:
        print(f"\n  mean sunrise deviation {sum(rise_d)/len(rise_d):+.2f} min")
    if set_d:
        print(f"  mean sunset  deviation {sum(set_d)/len(set_d):+.2f} min")
    print("  A one-signed, similar-sized offset is the expected signature of")
    print("  the upper-limb versus centre convention, not an error.\n")


def check_civil_twilight(failures):
    print("=" * 78)
    print("PART A3  Civil twilight, reported separately")
    print("=" * 78)
    print("  Both sides mark this by the sun's CENTRE at -6 deg, so the")
    print("  one-signed offset seen in the rise/set rows should NOT appear.")
    print(f"  Tolerance {CIVIL_TOLERANCE_MIN:.0f} min.\n")

    local_failures = []
    for iso, cb, _r, _t, _s, ce in USNO:
        date = dt.date.fromisoformat(iso)
        up, down = crossings(date, REFERENCE_TZ, CIVIL_ALTITUDE)
        print(f"  {iso}")
        _row("civil twilight begin", up, cb, date, CIVIL_TOLERANCE_MIN,
             local_failures)
        _row("civil twilight end", down, ce, date, CIVIL_TOLERANCE_MIN,
             local_failures)
        print()
    failures.extend(local_failures)


# ---------------------------------------------------------------------------
# PART B: internal invariants, no external source needed
# ---------------------------------------------------------------------------

def check_invariants(year, failures):
    print("=" * 78)
    print(f"PART B  Internal invariants ({year})")
    print("=" * 78)

    # 1. Declination cannot exceed the axial tilt, about 23.44 degrees.
    decs = []
    day = dt.date(year, 1, 1)
    while day.year == year:
        decs.append(solar_declination(dt.datetime.combine(day, dt.time(12, 0))))
        day += dt.timedelta(days=1)
    worst = max(abs(d) for d in decs)
    ok = worst <= 23.44
    print(f"  declination within +/-23.44 deg      max |dec| {worst:6.3f}   "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        failures.append("declination bound")

    # 2. Declination must pass through zero at the equinoxes.
    for name, date in (("March equinox", g.march_equinox(year)),
                       ("September equinox", g.september_equinox(year))):
        d = solar_declination(dt.datetime.combine(date, dt.time(19, 0)))
        ok = abs(d) < 0.5
        print(f"  {name:20s} {date}  dec {d:+6.3f}   "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            failures.append(name)

    # 3. On a flat horizon, sunrise and sunset are symmetric about solar noon.
    #    Not exactly, because declination shifts slightly during the day, so a
    #    minute of asymmetry is physical rather than a bug.
    for iso, *_ in USNO:
        date = dt.date.fromisoformat(iso)
        up, down = crossings(date, REFERENCE_TZ)
        if up is None or down is None:
            continue
        midpoint = up + (down - up) / 2
        off = abs((midpoint - transit(date, REFERENCE_TZ)).total_seconds()) / 60
        ok = off < 1.5
        print(f"  sunrise/sunset symmetric {iso}  midpoint off solar noon by "
              f"{off:4.2f} min   {'PASS' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"symmetry {iso}")
    print()


# ---------------------------------------------------------------------------

def run_all(year=None):
    """Run every check. Returns True if all passed."""
    year = year or g.ANALYSIS_YEAR
    failures, rise_d, set_d = check_against_usno()
    check_convention_signature(rise_d, set_d, failures)
    check_civil_twilight(failures)
    check_invariants(year, failures)

    print("=" * 78)
    if failures:
        print(f"RESULT: {len(failures)} CHECK(S) FAILED")
        for f in failures:
            print(f"  - {f}")
    else:
        print("RESULT: ALL CHECKS PASSED")
    print("=" * 78)
    return not failures


if __name__ == "__main__":
    raise SystemExit(0 if run_all() else 1)
