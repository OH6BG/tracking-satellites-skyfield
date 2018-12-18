from skyfield.api import Topos, load

ts = load.timescale()
t = ts.now()

# Observer coordinates
lat, lon = 63.146, 21.542
# Observer date
year, month, day = 2018, 12, 18

i, refreshed, sat_list = 0, False, []
sat_file = "amateur_satellite_times_%s-%s-%s.txt" % (year, month, day)
stations_url = 'https://www.celestrak.com/NORAD/elements/amateur.txt'
satellites = load.tle(stations_url)
qth = Topos(lat, lon)

res = "AMATEUR SATELLITE TIMES FOR LOCATION: %s, %s" % (lat, lon)
print(res)
print("Date:", "-".join([str(year), str(month), str(day)]), "\n")

for sat in satellites:

    if isinstance(sat, int):
        continue

    satellite = satellites[sat]
    sid = str(satellite).rsplit(' ', 2)[1].split("=")[1]

    if sid not in sat_list:
        sat_list.append(sid)
    else:
        continue

    difference = satellite - qth
    days = t - satellite.epoch

    if abs(days) > 2 and not refreshed:
        satellites = load.tle(stations_url, reload=True)
        refreshed = True
        satellite = satellites[sat]
        difference = satellite - qth
        days = t - satellite.epoch

    i += 1
    print("Processing [%02d] %s: %.3f days away from epoch" % (i, sat, days))
    res += "\n%s: %.3f days away from epoch\n" % (sat, days)
    res += "%-16s  %3s  %-4s  %5s\n" % ("DATETIME",
        "ALT",
        "AZIM",
        "KM",)

    sep = True

    for hh in range(24):

        for mm in range(60):

            t = ts.utc(year, month, day, hh, mm)
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()

            if alt.degrees < -0.5:
                sep = True
            else:
                if sep:
                    res += "%s\n" % ("-" * 34)
                    sep = False

                res += "%s  %2d°  %3d°  %5d\n" % (t.utc_strftime('%Y-%m-%d %H:%M'),
                    round(alt.degrees),
                    round(az.degrees),
                    round(distance.km),)

with open(sat_file, 'w', encoding='utf-8') as outfile:
    outfile.write(res)

print("Writing satellite times to: %s" % sat_file)
