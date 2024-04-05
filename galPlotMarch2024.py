#import loadGalileo
from galileo_loader import product, variable
import datetime
import xarray as xr
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
from swdb_tables import kp

pa0207 = product(
    name="Galileo GSAT0207 EMU data",
    description="Processed flux data from Ingmar Sandberg's analysis of GSAT0207 data",
    instrument="emu",
    satellite="gsat0207",
    level=1,
    version=1,
    variables={
        'Epoch': variable(
            name='Accumulation interval centre epoch',
            key='Epoch',
        ),
        'FEDO_Energy': variable(
            name='Electron Energy',
            key='FEDO_Energy',
        ),
        'FEDO': variable(
            name='Electron_differential_omni-directional',
            key='FEDO',
        ),
        'ODI_Position': variable(
            name='Electron_differential_omni-directional',
            key='ODI_Position',
        ),
        'ODI_unilib_L_star': variable(
            name='Electron_differential_omni-directional',
            key='ODI_Lstar',
        ),
        'ODI_unilib_L': variable(
            name='Electron_differential_omni-directional',
            key='ODI_L',
        ),
    },
    dataset=xr.Dataset()
)

pa0215 = product(
    name="Galileo GSAT0215 EMU data",
    description="Processed flux data from Ingmar Sandberg's analysis of GSAT0215 data",
    instrument="emu",
    satellite="gsat0215",
    level=1,
    version=1,
    variables={
        'Epoch': variable(
            name='Accumulation interval centre epoch',
            key='Epoch',
        ),
        'FEDO_Energy': variable(
            name='Electron Energy',
            key='FEDO_Energy',
        ),
        'FEDO': variable(
            name='Electron_differential_omni-directional',
            key='FEDO',
        ),
        'ODI_Position': variable(
            name='Electron_differential_omni-directional',
            key='ODI_Position',
        ),
        'ODI_unilib_L_star': variable(
            name='Electron_differential_omni-directional',
            key='ODI_Lstar',
        ),
        'ODI_unilib_L': variable(
            name='Electron_differential_omni-directional',
            key='ODI_L',
        ),
    },
    dataset=xr.Dataset()
)

startDat = datetime.datetime(2024, 3, 19)
endDat = datetime.datetime(2024, 3, 26)
nDays = (endDat - startDat).days
dates = [startDat + datetime.timedelta(days=d) for d in range(nDays)]
energiesToPlot = [0.1, 0.5, 1, 2.5, 4.2]
#print(dates)
kpdb = kp.KpSelect()
kpRt = kpdb.select_potsdam_rt(startDat - datetime.timedelta(days=1), endDat + datetime.timedelta(days=1))

#print(pa0207)
pa0207.loadBS(dates)
pa0215.loadBS(dates)
#print(pa0207.dataset)

irbemDir = "/Users/matlang/PycharmProjects/twoLineElementHistorical/ODIPos/"
irbem0207File = f"{irbemDir}time_satGSAT0207_opt10000_20240319-20240326_kextOPQ77.nc"
irbem0215File = f"{irbemDir}time_satGSAT0215_opt10000_20240319-20240326_kextOPQ77.nc"

lStar0207 = xr.open_dataset(irbem0207File)
lStar0215 = xr.open_dataset(irbem0215File)

print(lStar0207.Lstar.values)
print(pa0207.dataset.ODI_unilib_L_star)

tsL0207 = [
    (t - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    for t in lStar0207.time.values
]
tsPa0207 = [
    (t - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    for t in pa0207.dataset.Epoch.values
]

interpLstar07 = np.interp(tsPa0207, tsL0207, np.array(lStar0207.Lstar.values, dtype=float))
pa0207.dataset.ODI_unilib_L_star[:] = interpLstar07

tsL0215 = [
    (t - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    for t in lStar0215.time.values
]
tsPa0215 = [
    (t - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    for t in pa0215.dataset.Epoch.values
]

interpLstar15 = np.interp(tsPa0215, tsL0215, np.array(lStar0215.Lstar.values, dtype=float))
pa0215.dataset.ODI_unilib_L_star[:] = interpLstar15

norm = mpl.colors.LogNorm(vmin=10 ** -2, vmax=10 ** 3)
im = mpl.cm.ScalarMappable(norm=norm)
fig, ax = plt.subplots(
    6, 1, sharex=True, figsize=(20, 11.25),
    gridspec_kw={'height_ratios': [3, 3, 3, 3, 3, 2]}
)
for j, ePlot in enumerate(energiesToPlot):
    print(ePlot)
    maskE = np.argmin(
        np.abs(pa0207.dataset.FEDO_Energy.values - ePlot)
    )

    try:
        ds0207LFilt = pa0207.dataset.where(pa0207.dataset.ODI_unilib_L_star>0)
        if ds0207LFilt.FEDO[:, maskE].size > 0:
            im = ax[j].scatter(
                ds0207LFilt.Epoch, ds0207LFilt.ODI_unilib_L_star, c=ds0207LFilt.FEDO[:, maskE] * 10e-3,
                norm=norm, cmap='viridis', s=10
            )
            # ax[j].set_title(f"E = {1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV")
            # ax.set_xlabel("Time")
            ax[j].set_ylabel(r"$L^*$")
            ax[j].set_ylim(4, 9)
    except:
        print("pa0207 dataset is empty")

    try:
        ds0215LFilt = pa0215.dataset.where(pa0215.dataset.ODI_unilib_L_star > 0)
        if ds0215LFilt.FEDO[:, maskE].size > 0:
            im = ax[j].scatter(
                ds0215LFilt.Epoch, ds0215LFilt.ODI_unilib_L_star, c=ds0215LFilt.FEDO[:, maskE] * 10e-3,
                norm=norm, cmap='viridis', s=10
            )
            # ax[j].set_title(f"E = {1000 * pa0215.dataset.FEDO_Energy.values[maskE]:.1f} keV")
            # ax.set_xlabel("Time")
            ax[j].set_ylabel(r"$L^*$")
    except:
        print("pa0215 dataset is empty")

    textBoxStr = f"{1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV"
    ax[j].text(
        1.02, 0.5, textBoxStr,
        transform=ax[j].transAxes, fontsize=14,
        verticalalignment='top'
    )

ax[-1].bar(
    kpRt[0, :], kpRt[1, :] / 10,
#    color='#007d01', label="Kp $\leq$ 3"
)
#ax[-1].legend(loc='upper right', bbox_to_anchor=(1.1, 1.25), fontsize=10, labelspacing=0.1, borderpad=0.1)
#print('endBar')
ax[-1].set_ylabel("KP")
ax[-1].set_xlim(startDat, endDat)
ax[-1].set_ylim(0, 9)
fig.subplots_adjust(left=0.05, right=0.82, top=0.97, bottom=0.03, wspace=0.1, hspace=0.1)
cbar_ax = fig.add_axes([0.92, 0.08, 0.02, 0.84])
fig.colorbar(im, cax=cbar_ax, label='Flux \n (cm$^{2}$ s keV)$^{-1}$')
plt.show()

fig, ax = plt.subplots(
    3, 1, sharex=True, figsize=(20, 11.25),
    gridspec_kw={'height_ratios': [3, 3, 2]}
)
for j, ePlot in enumerate(energiesToPlot):
    print(ePlot)
    maskE = np.argmin(
        np.abs(pa0207.dataset.FEDO_Energy.values - ePlot)
    )

    try:
        if pa0207.dataset.FEDO[:, maskE].size > 0:
            print((pa0207.dataset.FEDO[:, maskE] * 10e-3).min())
            ax[0].scatter(
                pa0207.dataset.Epoch, pa0207.dataset.FEDO[:, maskE] * 10e-3, s=5,
                label=f"{1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV"
            )
            # ax[j].set_title(f"E = {1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV")
            # ax.set_xlabel("Time")
            ax[0].set_ylabel("Flux \n (cm$^{2}$ s keV)$^{-1}$'")
            ax[0].set_yscale('log')
            ax[0].set_ylim(10 ** -4, 10 ** 6)
    except:
        print("pa0207 dataset is empty")

    try:
        if pa0215.dataset.FEDO[:, maskE].size > 0:
            ax[1].scatter(
                pa0215.dataset.Epoch, pa0215.dataset.FEDO[:, maskE] * 10e-3, s=5,
                label=f"{1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV"
            )
            # ax[j].set_title(f"E = {1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV")
            # ax.set_xlabel("Time")
            ax[1].set_ylabel("Flux \n (cm$^{2}$ s keV)$^{-1}$'")
            ax[1].set_yscale('log')
            ax[1].set_ylim(10 ** -4, 10 ** 6)
    except:
        print("pa0215 dataset is empty")

ax[0].text(
    1.02, 0.5, "GSAT0207",
    transform=ax[0].transAxes, fontsize=14,
    verticalalignment='top'
)
ax[1].text(
    1.02, 0.5, "GSAT0215",
    transform=ax[1].transAxes, fontsize=14,
    verticalalignment='top'
)
ax[0].text(
    1.03, 1.1, "Galileo\nsatellite",
    transform=ax[0].transAxes, fontsize=14, verticalalignment='top'
)
ax[0].legend(
    loc='upper right', bbox_to_anchor=(1.1, 0.94), fontsize=10,
    title='GSAT0207 Energy', title_fontsize=11,
    labelspacing=0.1, borderpad=0.1
)
ax[1].legend(loc='upper right', bbox_to_anchor=(1.1, 0.94), fontsize=10,
    title='GSAT0215 Energy', title_fontsize=11,
    labelspacing=0.1, borderpad=0.1
)
plt.show()

###########################################################################
LsToPlot = [5.0, 6.0, 7.0]
for j, ePlot in enumerate(energiesToPlot):
    print(ePlot)
    maskE = np.argmin(
        np.abs(pa0207.dataset.FEDO_Energy.values - ePlot)
    )

    fig, ax = plt.subplots(
        len(LsToPlot) + 1, 1, sharex=True, figsize=(20, 11.25),
        gridspec_kw={'height_ratios': [3, 3, 3, 2]}
    )
    for il, lPlot in enumerate(LsToPlot):
        maskL = np.argmin(
            np.abs(pa0207.dataset.ODI_unilib_L_star.values - lPlot)
        )
        try:
            if pa0207.dataset.FEDO[:, maskE].size > 0:
                print((pa0207.dataset.FEDO[:, maskE] * 10e-3).min())
                ax[il].scatter(
                    pa0207.dataset.Epoch, pa0207.dataset.FEDO[:, maskE] * 10e-3, s=5,
                    label=f"{1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV"
                )
                # ax[j].set_title(f"E = {1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV")
                # ax.set_xlabel("Time")
                ax[il].set_ylabel("Flux \n (cm$^{2}$ s keV)$^{-1}$'")
                ax[il].set_yscale('log')
                ax[il].set_ylim(10 ** -4, 10 ** 6)
        except:
            print("pa0207 dataset is empty")

        try:
            if pa0215.dataset.FEDO[:, maskE].size > 0:
                ax[il].scatter(
                    pa0215.dataset.Epoch, pa0215.dataset.FEDO[:, maskE] * 10e-3, s=5,
                    label=f"{1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV"
                )
                # ax[j].set_title(f"E = {1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV")
                # ax.set_xlabel("Time")
                ax[il].set_ylabel("Flux \n (cm$^{2}$ s keV)$^{-1}$'")
                ax[il].set_yscale('log')
                ax[il].set_ylim(10 ** -4, 10 ** 6)
        except:
            print("pa0215 dataset is empty")

    plt.show()
ax[0].text(
    1.02, 0.5, "GSAT0207",
    transform=ax[0].transAxes, fontsize=14,
    verticalalignment='top'
)
ax[1].text(
    1.02, 0.5, "GSAT0215",
    transform=ax[1].transAxes, fontsize=14,
    verticalalignment='top'
)
ax[0].text(
    1.03, 1.1, "Galileo\nsatellite",
    transform=ax[0].transAxes, fontsize=14, verticalalignment='top'
)
ax[0].legend(
    loc='upper right', bbox_to_anchor=(1.1, 0.94), fontsize=10,
    title='GSAT0207 Energy', title_fontsize=11,
    labelspacing=0.1, borderpad=0.1
)
ax[1].legend(loc='upper right', bbox_to_anchor=(1.1, 0.94), fontsize=10,
    title='GSAT0215 Energy', title_fontsize=11,
    labelspacing=0.1, borderpad=0.1
)
plt.show()