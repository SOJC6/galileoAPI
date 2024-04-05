import numpy as np
from skyfield.api import load, wgs84, EarthSatellite
import datetime
from io import BytesIO
from skyfield.iokit import parse_tle_file

n = 41859
ts = load.timescale()
print(ts.now())

# Time to find satellite position
t = ts.utc(2024, 3, 17, 12, 0, 0)
tDt = datetime.datetime.strptime(
    t.utc_strftime("%Y-%m-%d %H:%M:S"), "%Y-%m-%d %H:%M:S"
)

if np.abs(ts.now() - t) < 14:
    # Download most recent data
    url = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={n}'
    filename = f"tle-CATNR-{n}-{t.utc_strftime('%Y-%m-%d')}.txt"
    satellites = load.tle_file(url, filename=filename)
    print(satellites)

    # Read in the two-line element
    with open(filename, 'r') as f:
        satLns = f.readlines()
else:
    # Read in historical TLEs from file
    filename = f"/Users/matlang/PycharmProjects/twoLineElementHistorical/sat0000{n}.txt"

    with open(filename, 'r') as f:
        histSatLns = f.readlines()

    yearStr = [f"20{h[18:20]}" for i, h in enumerate(histSatLns) if i%2 == 0]
    doyStr = [float(h[20:32]) for i, h in enumerate(histSatLns) if i%2 == 0]
    dtStr = np.array([
        datetime.datetime.strptime(f"20{h[18:20]} {int(float(h[20:32]))}", "%Y %j")
        for i, h in enumerate(histSatLns) if i%2 == 0
    ])
    diffTime = [
        (tDt - d).total_seconds() for d in dtStr
    ]
    diffTime = [
        d if d >= 0 else 1e31 for d in diffTime
    ]
    print(diffTime)
    argReq = np.argmin(np.abs(diffTime))
    print(dtStr[argReq])
    print(histSatLns[2*argReq])

    # Define a string for the name of the satellite
    if n == 41859:
        satName = "GSAT0207 (GALILEO 15)"
    elif n == 43055:
        satName = "GSAT0215 (GALILEO 19)"
    else:
        satName = ""

    satLns = [
        satName, histSatLns[2*argReq], histSatLns[(2 * argReq) + 1]
    ]

print(satLns)
eSat = EarthSatellite(satLns[1], satLns[2], satLns[0], ts)
print(eSat)

# t = ts.utc(2024, 3, 17, 12, 0, 0)

days = t - eSat.epoch
print('{:.3f} days away from epoch'.format(days))

geocentric = eSat.at(t)
print(geocentric.position.km)