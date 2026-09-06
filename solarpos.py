"""
Solar position (altitude + azimuth) using the NOAA Solar Calculator algorithm.

Everything here is pure arithmetic on the date -- no data files, no network.
The output is: given a place on Earth and a moment in time, where is the sun
in the sky? Two numbers:

    altitude  = degrees above the horizontal  (negative = below the horizon)
    azimuth   = degrees clockwise from true north (0=N, 90=E, 180=S, 270=W)

We need BOTH, because a mountain horizon is not a flat line. The ridge height
depends on which direction you look, so to know whether the sun is visible we
have to know where in the sky it is, not just how high.
"""

import math
import datetime as dt


def _julian_day(when_utc: dt.datetime) -> float:
    """Convert a UTC datetime to a Julian Day number (days since 4713 BC).

    Astronomy runs on this instead of calendars because it is one continuous
    number with no months, leap years or time zones to trip over.
    """
    y, m = when_utc.year, when_utc.month
    d = (when_utc.day
         + when_utc.hour / 24
         + when_utc.minute / 1440
         + when_utc.second / 86400)
    if m <= 2:                      # Jan/Feb count as months 13/14 of the prior year
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4              # Gregorian calendar correction
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def _ecliptic(t: float):
    """Shared first half of the NOAA sequence, for Julian centuries `t`.

    Returns (apparent_longitude, corrected_obliquity, mean_longitude,
    mean_anomaly), all in degrees. Both sun_position and solar_declination
    need this, and computing it in one place stops the two drifting apart.
    """
    # Mean longitude: where the sun WOULD be if Earth's orbit were a circle.
    mean_long = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360
    # Mean anomaly: how far Earth is around its orbit from perihelion.
    mean_anom = 357.52911 + t * (35999.05029 - 0.0001537 * t)
    ma = math.radians(mean_anom)
    # Equation of centre: the correction for the orbit actually being elliptical.
    centre = (math.sin(ma) * (1.914602 - t * (0.004817 + 0.000014 * t))
              + math.sin(2 * ma) * (0.019993 - 0.000101 * t)
              + math.sin(3 * ma) * 0.000289)
    true_long = mean_long + centre
    # Apparent longitude also folds in nutation (a small wobble of Earth's axis).
    omega = 125.04 - 1934.136 * t
    app_long = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    # --- Tilt of Earth's axis ---------------------------------------------
    sec = 21.448 - t * (46.8150 + t * (0.00059 - t * 0.001813))
    obliq = 23.0 + (26.0 + sec / 60.0) / 60.0
    obliq_corr = obliq + 0.00256 * math.cos(math.radians(omega))

    return app_long, obliq_corr, mean_long, mean_anom


def solar_declination(when_utc: dt.datetime) -> float:
    """How far north (+) or south (-) of the equator the sun stands, degrees.

    Depends only on the moment, not on where you are standing. It reaches its
    minimum at the December solstice and its maximum at the June solstice, and
    passes through zero at the equinoxes, which is how those dates are found.
    """
    t = (_julian_day(when_utc) - 2451545.0) / 36525.0
    app_long, obliq_corr, _, _ = _ecliptic(t)
    lam, eps = math.radians(app_long), math.radians(obliq_corr)
    return math.degrees(math.asin(math.sin(eps) * math.sin(lam)))


def sun_position(when_utc: dt.datetime, lat_deg: float, lon_deg: float):
    """Return (altitude_deg, azimuth_deg) of the sun's centre.

    lon_deg is negative west of Greenwich (Golden is about -116.96).
    """
    jd = _julian_day(when_utc)
    t = (jd - 2451545.0) / 36525.0          # Julian centuries since J2000.0

    app_long, obliq_corr, mean_long, mean_anom = _ecliptic(t)

    # --- Convert ecliptic position to sky coordinates ----------------------
    lam, eps = math.radians(app_long), math.radians(obliq_corr)
    declination = math.degrees(math.asin(math.sin(eps) * math.sin(lam)))

    # Equation of time: clocks tick evenly, the sun does not. This is the
    # gap between them, in minutes -- up to about +/-16 minutes over the year.
    var_y = math.tan(eps / 2) ** 2
    gml, gma = math.radians(mean_long), math.radians(mean_anom)
    ecc = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
    eot = 4 * math.degrees(
        var_y * math.sin(2 * gml)
        - 2 * ecc * math.sin(gma)
        + 4 * ecc * var_y * math.sin(gma) * math.cos(2 * gml)
        - 0.5 * var_y * var_y * math.sin(4 * gml)
        - 1.25 * ecc * ecc * math.sin(2 * gma)
    )

    # --- Hour angle: how far the sun is from due south, in degrees ---------
    minutes_utc = when_utc.hour * 60 + when_utc.minute + when_utc.second / 60
    true_solar_min = (minutes_utc + eot + 4 * lon_deg) % 1440
    hour_angle = true_solar_min / 4 - 180        # 0 deg = solar noon

    # --- Spherical trig: turn that into altitude and azimuth ---------------
    lat, dec, ha = map(math.radians, (lat_deg, declination, hour_angle))
    cos_zenith = (math.sin(lat) * math.sin(dec)
                  + math.cos(lat) * math.cos(dec) * math.cos(ha))
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    zenith = math.degrees(math.acos(cos_zenith))
    altitude = 90.0 - zenith

    # Atmospheric refraction bends light over the horizon, so the sun LOOKS
    # higher than it geometrically is -- about 34 arcminutes at the horizon.
    altitude += _refraction(altitude)

    denom = math.cos(math.radians(zenith)) * math.sin(lat) - math.sin(dec)
    if abs(denom) < 1e-12:
        azimuth = 180.0
    else:
        az = math.degrees(math.acos(max(-1.0, min(1.0,
             ((math.sin(lat) * math.cos(math.radians(zenith))) - math.sin(dec))
             / (math.cos(lat) * math.sin(math.radians(zenith)))))))
        azimuth = (az + 180) % 360 if hour_angle > 0 else (540 - az) % 360

    return altitude, azimuth


def _refraction(alt_deg: float) -> float:
    """Apparent lift of the sun caused by the atmosphere, in degrees."""
    if alt_deg > 85.0:
        return 0.0
    a = math.radians(alt_deg)
    if alt_deg > 5.0:
        c = (58.1 / math.tan(a) - 0.07 / math.tan(a) ** 3
             + 0.000086 / math.tan(a) ** 5)
    elif alt_deg > -0.575:
        c = 1735 + alt_deg * (-518.2 + alt_deg * (103.4
            + alt_deg * (-12.79 + alt_deg * 0.711)))
    else:
        c = -20.772 / math.tan(a)
    return c / 3600.0
