import numpy as np
import datetime
import xarray as xr

# Read the OMNI file and extract the data
with open("/Users/matlang/PycharmProjects/apiLoader/omni20170101-20240206.lst") as f:
    omniLines = f.readlines()

# Initialise lists
dates = []
bzList = []
swSpeed = []
kpList = []
dstList = []

# Iterate and extract variables from lines
for i, li in enumerate(omniLines):
    s = li.split()

    # Create dates
    year = int(s[0].strip())
    doY = int(s[1].strip())
    hr = int(s[2].strip())
    dat = (
        datetime.datetime(year, 1, 1)
        + datetime.timedelta(days=doY - 1)
        + datetime.timedelta(hours=hr)
    )

    # Create variables
    bz = float(s[3].strip())
    vsw = float(s[4].strip())
    kp = float(s[5].strip()) / 10.0
    dst = int(s[6].strip())

    # Append data to lists
    dates.append(dat)
    bzList.append(bz)
    swSpeed.append(vsw)
    kpList.append(kp)
    dstList.append(dst)

# Create dataset
ds = xr.Dataset(
    data_vars=dict(
        bz=(["time"], bzList),
        swSpeed=(["time"], swSpeed),
        kp=(["time"], kpList),
        dst=(["time"], dstList),
    ),
    coords=dict(
        time=(["time"], dates)
    )
)

filePath_nc = "/Users/matlang/PycharmProjects/apiLoader/omniData.nc"
ds.to_netcdf(path=filePath_nc, mode='w')