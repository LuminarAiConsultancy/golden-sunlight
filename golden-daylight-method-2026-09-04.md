# Method statement: true sun-on-town times for Golden, BC
### Prepared 4 September 2026, for independent verification

Everything another person or system needs to check this work, without access to the
original code.

---

## 1. The question

Published sunrise and sunset tables assume a flat horizon. Golden sits on the floor of
the Columbia Valley with mountains on both sides, so the sun is already well up before
it clears the ridge, and it disappears behind the opposite ridge well before it sets.
The task was to calculate when direct sunlight actually reaches the townsite, and to do
it twice: once for permanent Mountain Standard Time (UTC minus 7) and once for permanent
Mountain Daylight Time (UTC minus 6).

## 2. Inputs

- Observation point: 51.2969 degrees north, 116.9647 degrees west. Golden townsite.
- Observer eye height: 1.6 metres above ground level.
- Elevation data: AWS Terrain Tiles ('skadi'), 1 arc-second, roughly 30 metres per
  sample. SRTM-derived and void-filled, not raw SRTMGL1. Four tiles mosaicked
  (N50W117, N50W118, N51W117, N51W118), giving a 7200 by 7200 grid. Elevations
  sampled by bilinear interpolation between grid points. Voids are skipped, not
  filled, which biases computed ridge heights DOWN.
- Search radius: 60 kilometres in every direction.

## 3. Building the horizon profile

For each of 720 compass bearings (every 0.5 degrees from 0 to 359.5):

1. Step outward from the observer along that bearing in 40-metre increments, to
   60 kilometres. That is 1,500 sample points per bearing.
2. At each sample point, read the ground elevation from the interpolated grid.
3. Subtract the amount that point sinks below a straight sightline because the Earth
   curves away and because the atmosphere bends light slightly downward:

       drop = d^2 * (1 - k) / (2 * R)

   where `d` is distance in metres, `R` is 6,371,000 metres (mean Earth radius), and
   `k` is 0.13, the standard atmospheric refraction coefficient.

4. Compute the apparent angle of that point above the observer's horizontal:

       angle = atan2(elevation - observer_elevation - drop, d)

5. Take the maximum angle along the whole ray. That is the horizon angle for that
   bearing. Floor it at 0 degrees, since the sea-level horizon is the minimum case.

The result is a lookup table mapping bearing to horizon angle. Values in between the
720 bearings are linearly interpolated, wrapping around at 360 degrees.

**Result for Golden:** highest ridge 12.2 degrees, at bearing 240 degrees (south-west).
At the eight cardinal and intercardinal points: north 5.6, north-east 9.1, east 5.5,
south-east 5.2, south 6.9, south-west 9.1, west 9.4, north-west 1.9 degrees.

## 4. Solar position

Sun altitude and azimuth computed with the NOAA Solar Calculator algorithm. The
sequence, for a given UTC instant:

1. Convert the calendar date and time to a Julian Day number.
2. `t` = Julian centuries since J2000.0, that is `(JD - 2451545.0) / 36525`.
3. Geometric mean longitude of the sun:
   `280.46646 + t*(36000.76983 + t*0.0003032)`, modulo 360.
4. Geometric mean anomaly: `357.52911 + t*(35999.05029 - 0.0001537*t)`.
5. Equation of centre (correction for the elliptical orbit):
   `sin(M)*(1.914602 - t*(0.004817 + 0.000014*t)) + sin(2M)*(0.019993 - 0.000101*t)
   + sin(3M)*0.000289`.
6. True longitude = mean longitude + equation of centre. Apparent longitude then
   subtracts `0.00569 + 0.00478*sin(omega)` for nutation and aberration, where
   `omega = 125.04 - 1934.136*t`.
7. Mean obliquity of the ecliptic from the standard series, corrected by
   `+0.00256*cos(omega)`.
8. Declination: `asin(sin(obliquity) * sin(apparent longitude))`.
9. Equation of time by the `var_y` method, where `var_y = tan(obliquity/2)^2`, giving
   the offset in minutes between clock time and true solar time.
10. True solar time, then hour angle = `true_solar_minutes / 4 - 180`.
11. Altitude from spherical trigonometry:
    `sin(alt) = sin(lat)*sin(dec) + cos(lat)*cos(dec)*cos(hour_angle)`.
12. Azimuth derived from the same triangle, resolved to 0 to 360 degrees clockwise
    from true north using the sign of the hour angle.
13. Atmospheric refraction added to the altitude, using the standard piecewise
    approximation (about 34 arcminutes of lift at the horizon, falling to nothing
    overhead).

## 5. The visibility test

The sun is counted as being on the town at a given moment when:

    solar altitude at that moment  >  horizon angle at the sun's azimuth at that moment

Sampled every minute across the full local day. The first minute the test passes is
"sun on". The last minute it passes is "sun off". Total daylight is the count of
passing minutes divided by 60, which correctly handles any case where a ridge
interrupts the sun mid-day.

For the annual day-counts the sampling interval was 2 minutes, for speed, across all
365 days of 2027.

The two time options differ only by the UTC offset applied when converting local clock
time to UTC. Nothing else changes, which is why the daylight totals are identical
between them.

## 6. Validation performed

**Check one, solar geometry against published values.** Golden, 13 July 2025:

| Quantity | Published | Calculated |
|---|---|---|
| Solar noon altitude | 60.4 deg | 60.40 deg |
| Sunrise azimuth | 52 deg | 52.24 deg |
| Sunset azimuth | 307 deg | 307.42 deg |

**Check two, whole pipeline with terrain switched off.** The same program run with the
horizon angle forced to 0 at every bearing reproduced standard almanac sunrise and
sunset for Golden within two to three minutes, and produced identical day lengths under
both time options. The residual two to three minutes is a known convention difference:
almanacs mark sunrise when the sun's upper edge touches the horizon, this marks when
the sun's centre clears the skyline, which is the appropriate test for direct light
reaching the ground.

Only after both checks passed was the real terrain used.

## 7. Results

Winter solstice, 21 December 2026, at the townsite. Other dates and all annual
counts are for calendar year 2027 (365 days).

| | Sun on | Sun off | Direct sun |
|---|---|---|---|
| Standard time (UTC-7) | 9:35 am | 3:26 pm | 5 h 52 m |
| Daylight time (UTC-6) | 10:35 am | 4:26 pm | 5 h 52 m |
| Flat horizon, standard | 8:53 am | 4:39 pm | 7 h 47 m |
| Flat horizon, daylight | 9:53 am | 5:39 pm | 7 h 47 m |

Terrain removes 42 minutes from the morning and 73 minutes from the afternoon, under
either option equally.

Days per year the sun has not cleared the ridge by a given clock time:

| Threshold | Standard, real | Daylight, real | Standard, flat | Daylight, flat |
|---|---|---|---|---|
| 8:00 am | 166 | 201 | 98 | 160 |
| 9:00 am | 104 | 166 | 0 | 98 |
| 10:00 am | 0 | 104 | 0 | 0 |

## 8. Known limitations

1. One observation point. Other parts of town, and the benches, will differ.
2. The data is a surface model. Canopy on distant ridgelines makes them too tall and
   overstates the effect; canopy or structures at the observation point raise the
   sightline origin and understate it; obstructions within about 30 metres are absent
   entirely. Net direction of bias is NOT established.
3. Clear-sky direct sun only. Valley cloud and December inversions are not modelled.
4. Sample points along each ray use a planar approximation with the longitude scale
   frozen at the observer's latitude, giving up to 424 m of positional error at 60 km
   on diagonal bearings.
5. The refraction coefficient is the standard 0.13. Winter temperature inversions bend
   light more than this, which would place true sunrise slightly earlier than shown.
6. The annual day-counts use 2-minute sampling, so individual days near a threshold
   could be off by one sample.

---

## Suggested verification prompt

Asking a language model whether a method "looks right" will almost always get agreement,
which proves nothing. Ask it to do the work instead. Something like:

> Below is a method statement for calculating when direct sunlight reaches a valley
> townsite, allowing for surrounding terrain. Do three things. First, independently
> compute solar altitude and azimuth for Golden BC at 51.2969 N, 116.9647 W for 21
> December 2026 at 9:35 am and at 3:26 pm under UTC minus 7, and tell me whether the
> sun's altitude at those moments is consistent with a ridge of roughly 5 to 7 degrees
> in the relevant directions. Second, identify any error in the physics or the formulas
> as stated, particularly the curvature and refraction correction and the equation of
> time. Third, list what would make these results wrong that the limitations section
> does not already name. Do not summarise the method back to me.

Be aware of what it can and cannot check. The solar arithmetic is fully checkable, since
it needs no data. The horizon angles are not checkable without the elevation tiles, so
unless it can download the data and run code, it can only assess whether the approach is
sound, not whether 12.2 degrees at bearing 240 is the correct number for Golden.

The elevation data is free and public: 1 arc-second SRTM tiles N50W117, N50W118,
N51W117 and N51W118, available from USGS EarthExplorer or viewfinderpanoramas.org.
