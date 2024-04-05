from cdflib import xarray as cxr
import xarray as xr
import matplotlib.pyplot as plt
import datetime
import os
import netCDF4 as nc
import numpy as np
import gzip

plt.rcParams.update({'font.size': 16})

startDate = datetime.datetime(2024, 1, 9)
endDate = datetime.datetime(2024, 1, 21)

nDays = (endDate - startDate).days
dates = [startDate + datetime.timedelta(days=d) for d in range(nDays)]
ds = False
dataFolder = "/Users/matlang/PycharmProjects/galileoDataDownload/gsat0207/2024/"

for d, dat in enumerate(dates):
    print(dat)
    strDate = dat.strftime("%Y%m%d")
    fileName = f"galileo_gssc_emu_gsat0207_sd_l1_{strDate}_V01.cdf"

    dataFile = os.path.join(dataFolder, fileName)
    #try:
    # if os.path.isfile(dataFile):
    #     pass
    # elif os.path.isfile(f"{dataFile}.gz"):
    #     with gzip.open(dataFile, 'rb') as f:
    #         os.system('gunzip ' + dataFile)
    # else:
    #     print(f"")
    if not ds:
        ds = cxr.cdf_to_xarray(dataFile, to_datetime=True)
        print(list(ds.variables))
        for var in ds.variables:
            print(f"{var}: {ds[var].attrs}")
        #sys.exit()
        ds = ds.where((ds.FEDO > -1))
        ds = ds.resample(Epoch='1H').mean()
    else:
        #with gzip.open(dataFile, 'rb') as f:
        ds2 = cxr.cdf_to_xarray(dataFile, to_datetime=True)
        ds2 = ds2.where((ds2.FEDO > -1))
        ds2 = ds2.resample(Epoch='1H').mean()

        ds = xr.concat([ds, ds2], dim="Epoch")
    # except:
    #    print(f"{dataFile} does not exist. Moving to next date.")

#print(ds['Epoch'].where((ds.Epoch > np.datetime64('2024-01-16'))))
#sys.exit()
for i in range(3):
    plt.plot(ds.Epoch, ds.ODI_unilib_L_star.where(ds.ODI_unilib_L_star > -1)[:])
plt.show()
da = ds['FEDO']
print(1000 * ds.FEDO_Energy.values)
fig, ax = plt.subplots(3, 1, sharex=True)
for i in range(8):
    ax[0].plot(ds.Epoch, ds.ODI_Position.values[:, 0, 0])
    ax[1].plot(ds.Epoch, ds.ODI_Position.values[:, 1, 0])
    ax[2].plot(ds.Epoch, ds.ODI_Position.values[:, 2, 0])
    plt.show()
sys.exit()
dsRoll = da.rolling(Epoch=14).mean()
print(dsRoll)
    #ds = cxr.cdf_to_xarray('galileo_gssc_emu_gsat0207_sd_l1_20170201_V01.cdf')
#cdf_to_xarray('galileo_gssc_emu_gsat0207_sd_l1_20221205_V01.cdf')
# print(ds.FEDO)
colour = ['b', 'r', 'g', 'c', 'm', 'lime', 'teal', 'k', 'y', 'pink', 'w']
fig, ax = plt.subplots(2, 1, sharex=True)
for i in range(8):
    legendStr = ds.FEDO_Energy[i].values * 1000
    ax[0].semilogy(ds.Epoch, ds.FEDO[:, i], color=colour[i], label=f"{legendStr:.2f} keV")
#ax[0].set_xlabel("Time")
ax[0].set_ylabel("Flux (cm^-2 s^-1 sr^-1 MeV^-1)")
ax[0].set_title("Raw flux from GSAT0207")
ax[0].legend(bbox_to_anchor=(1.01, 1))
#plt.show()

#fig, ax = plt.subplots(1, 1)
for i in range(8):
    legendStr = ds.FEDO_Energy[i].values * 1000
    ax[1].semilogy(dsRoll.Epoch, dsRoll[:, i], color=colour[i], label=f"{legendStr:.2f} keV")
ax[1].set_xlabel("Time")
ax[1].set_ylabel("Flux (cm^-2 s^-1 sr^-1 MeV^-1)")
ax[1].set_title("14 hr rolling mean of flux from GSAT0207")
#plt.legend(bbox_to_anchor=(1.01, 1))
plt.show()
