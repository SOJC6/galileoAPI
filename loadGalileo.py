from galileo_loader import product, variable
import datetime
from dateutil.rrule import rrule, MONTHLY, YEARLY
from dateutil import relativedelta
import xarray as xr
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import sys
from swdb_tables import kp

sys.path.append("/Users/matlang/PycharmProjects/datetimeConv/")
import conversions

plt.rcParams.update({"font.size": 14})

def plotContour(
        pa0207, pa0215, omniDs, energiesToPlot, outputDir, startDat, endDat, monthlyOrYearly
):
    """
    Plot the contour plots of galileo data and save to file

        Parameters
        ----------
        pa0207 : product class
            Contains Galileo GSAT0207 data
        pa0215 : product class
            Contains Galileo GSAT0215 data
        omniDs : xarray Dataset
            Dataset containing OMNI data (specifically, KP, Dst, Bz and SW Speed)
        energiesToPlot : list
            List containing energies to plot, the closest
            energies will be extracted from pa0207 and pa0215 rep.
        outputDir : str
            String containing the output directory
        startDat : datetime
            Start date to plot
        endDat : datetime
            End date to plot
        monthlyOrYearly: str
            String containing either 'monthly' or 'yearly', describing
            what the timescale of plot should be

        Returns
        -------
        None

    """
    norm = mpl.colors.LogNorm(vmin=10 ** -2, vmax=10 ** 4)
    im = mpl.cm.ScalarMappable(norm=norm)
    fig, ax = plt.subplots(
        7, 1, sharex=True, figsize=(20, 11.25),
        gridspec_kw={'height_ratios': [3, 3, 3, 3, 3, 2, 2]}
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
                ax[j].set_ylim(4.5, 10)
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
    ax[0].text(
        1.03, 1.1, "Energy",
        transform=ax[0].transAxes, fontsize=14, verticalalignment='top'
    )

    ax2 = ax[-2].twinx()
    ax2.plot(
        omniDs.time, omniDs.dst.where(omniDs.dst < 90000),
        color='black'
    )
    ax2.plot(
        [omniDs.time.values[0], omniDs.time.values[-1]], [0, 0],
        color='grey', linestyle='dashed'
    )
    ax2.set_ylabel("Dst\n(nT)")
    ax2.set_ylim(-250, 50)
    print('bar1')
    ax[-2].bar(
        omniDs.time, omniDs.kp.where(omniDs.kp <= 3),
        color='#007d01', label="Kp $\leq$ 3"
    )
    print('bar2')
    ax[-2].bar(
        omniDs.time, omniDs.kp.where((3 < omniDs.kp) & (omniDs.kp <= 5)),
        color='#b8bc00', label="3 < Kp $\leq$ 5"
    )
    print('bar3')
    ax[-2].bar(
        omniDs.time, omniDs.kp.where(omniDs.kp > 5),
        color='#fb0200', label="Kp > 5"
    )
    ax[-2].legend(loc='upper right', bbox_to_anchor=(1.1, 1.25), fontsize=10, labelspacing=0.1, borderpad=0.1)
    print('endBar')
    ax[-2].set_ylabel("KP")
    ax[-2].set_ylim(0, 9)

    ax1 = ax[-1].twinx()
    ax[-1].plot(
        omniDs.time, omniDs.bz.where(omniDs.bz < 999), color='black'
    )
    ax[-1].set_ylabel("IMF Bz\n(nT)")
    # ax[-2].set_xlabel("Time")
    ax[-1].set_ylim(-20, 20)

    ax1.plot(
        omniDs.time, omniDs.swSpeed.where(omniDs.swSpeed < 9999), color='red'
    )
    ax1.plot(
        [omniDs.time.values[0], omniDs.time.values[-1]], [500, 500],
        color='firebrick', linestyle='dashed'
    )
    ax1.set_ylabel("SW Speed\n(km/s)", color='red')
    ax1.tick_params(axis="y", labelcolor='red')
    ax1.set_ylim(200, 1000)
    ax[-1].set_xlim(startDat, endDat
                    )
    fig.subplots_adjust(left=0.05, right=0.82, top=0.97, bottom=0.03, wspace=0.1, hspace=0.1)
    cbar_ax = fig.add_axes([0.92, 0.08, 0.02, 0.84])
    fig.colorbar(im, cax=cbar_ax, label='Flux \n (cm$^{2}$ s keV)$^{-1}$')
    plt.savefig(f"{outputDir}/plots_0207_0215_Year2/{monthlyOrYearly}{startDat.strftime('%Y-%m')}.png")


def plotFluxTS(
    pa0207, pa0215, omniDs, energiesToPlot, outputDir, startDat, endDat, monthlyOrYearly
):
    fig, ax = plt.subplots(
        4, 1, sharex=True, figsize=(20, 11.25),
        gridspec_kw={'height_ratios': [3, 3, 2, 2]}
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
                    label = f"{1000 * pa0207.dataset.FEDO_Energy.values[maskE]:.1f} keV"
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

    ax2 = ax[-2].twinx()
    ax2.plot(
        omniDs.time, omniDs.dst.where(omniDs.dst < 90000),
        color='black'
    )
    ax2.plot(
        [omniDs.time.values[0], omniDs.time.values[-1]], [0, 0],
        color='grey', linestyle='dashed'
    )
    ax2.set_ylabel("Dst\n(nT)")
    ax2.set_ylim(-250, 50)
    print('bar1')
    ax[-2].bar(
        omniDs.time, omniDs.kp.where(omniDs.kp <= 3),
        color='#007d01', label="Kp $\leq$ 3"
    )
    print('bar2')
    ax[-2].bar(
        omniDs.time, omniDs.kp.where((3 < omniDs.kp) & (omniDs.kp <= 5)),
        color='#b8bc00', label="3 < Kp $\leq$ 5"
    )
    print('bar3')
    ax[-2].bar(
        omniDs.time, omniDs.kp.where(omniDs.kp > 5),
        color='#fb0200', label="Kp > 5"
    )
    ax[-2].legend(loc='upper right', bbox_to_anchor=(1.1, 1.0), fontsize=10, labelspacing=0.1, borderpad=0.1)
    print('endBar')
    ax[-2].set_ylabel("KP")
    ax[-2].set_ylim(0, 9)

    ax1 = ax[-1].twinx()
    ax[-1].plot(
        omniDs.time, omniDs.bz.where(omniDs.bz < 999), color='black'
    )
    ax[-1].set_ylabel("IMF Bz\n(nT)")
    # ax[-2].set_xlabel("Time")
    ax[-1].set_ylim(-20, 20)

    ax1.plot(
        omniDs.time, omniDs.swSpeed.where(omniDs.swSpeed < 9999), color='red'
    )
    ax1.plot(
        [omniDs.time.values[0], omniDs.time.values[-1]], [500, 500],
        color='firebrick', linestyle='dashed'
    )
    ax1.set_ylabel("SW Speed\n(km/s)", color='red')
    ax1.tick_params(axis="y", labelcolor='red')
    ax1.set_ylim(200, 1000)
    ax[-1].set_xlim(startDat, endDat)
    fig.subplots_adjust(left=0.1, right=0.9, top=0.97, bottom=0.03, wspace=0.1, hspace=0.1)
    # cbar_ax = fig.add_axes([0.92, 0.08, 0.02, 0.84])
    # fig.colorbar(im, cax=cbar_ax, label='Flux \n (cm$^{2}$ s keV)$^{-1}$')
    plt.savefig(f"{outputDir}/plots_0207_0215_TS/{monthlyOrYearly}{startDat.strftime('%Y-%m')}.png")


# Find current directory
currentDir = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({'font.size': 14})

startDate = datetime.datetime(2021, 1, 1, 0, 0, 0)
endDate = datetime.datetime(2024, 2, 1, 0, 0, 0)
monthlyOrYearly = 'monthly'
energiesToPlot = [0.1, 0.5, 1, 2.5, 4.2]

if ((monthlyOrYearly == 'monthly') or (monthlyOrYearly == 'yearly')):
    pass
else:
    print("Please enter 'monthly' or 'yearly'. Defaulting to monthly...")
    monthlyOrYearly = 'monthly'

rd = relativedelta.relativedelta(endDate, startDate)
nMonths = rd.months + (12 * rd.years)
nYears = rd.years

pa0207 = product(
    name="Galileo GSAT0207 EMU data",
    description="Processed flux data from Ingmar Sandberg's analysis of GSAT0207 data",
    instrument="emu",
    satellite="gsat0207",
    level=1,
    version=1,
    irbemCoords=True,
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

startDatList = []
endDatList = []

if monthlyOrYearly == 'monthly':
    for i, d in enumerate(rrule(MONTHLY, dtstart=startDate, until=endDate)):
        if i < nMonths:
            startDatList.append(d)

        if i > 0:
            endDatList.append(d)
    nIter = nMonths
elif monthlyOrYearly == 'yearly':
    for i, d in enumerate(rrule(YEARLY, dtstart=startDate, until=endDate)):
        if i < nMonths:
            startDatList.append(d)

        if i > 0:
            endDatList.append(d)
    nIter = nYears

print(startDatList)
print(endDatList)

# Read in OMNI dataset
omniFilePath = "/Users/matlang/PycharmProjects/apiLoader/omniData.nc"
omniDs = xr.open_dataset(omniFilePath)

for i in range(nIter):
    nDays = (endDatList[i] - startDatList[i]).days
    dates = [startDatList[i] + datetime.timedelta(days=d) for d in range(nDays)]

    print(pa0207)
    pa0207.loadBS(dates)#, variables=['FEDO'])
    pa0215.loadBS(dates)
    print(pa0207.dataset)
    # sys.exit()
    # Make time-series plots
    # fig, ax = plt.subplots(
    #     1, 1, figsize=(20, 5.5)
    # )
    # ax.plot(
    #     pa0215.dataset.Epoch, pa0215.dataset.ODI_unilib_L_star[:].where(pa0215.dataset.ODI_unilib_L_star > 0)
    # )
    # ax.set_xlabel("Time")
    # ax.set_ylabel("Lstar")
    # ax.set_xlim(datetime.datetime(2024, 3, 20), datetime.datetime(2024, 3, 10))
    # ax.set_ylim(3.5, 10)
    # ax.set_title("$L^{*}$ calculations for UNILIB for GALILEO GSAT0215")
    # plt.show()

    fig, ax = plt.subplots(
        1, 1, figsize=(20, 5.5)
    )
    ax.plot(
        pa0207.dataset.Epoch, pa0207.dataset.Lstar[:].where(pa0207.dataset.Lstar > 0)
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Lstar")
    ax.set_title("$L^{*}$ calculations for UNILIB for GALILEO GSAT0207")
    ax.set_xlim(datetime.datetime(2024, 1, 2), datetime.datetime(2024, 1, 31))
    ax.set_ylim(3.5, 10)
    plt.show()

    #######
    #Subplots
    # fig, ax = plt.subplots(
    #     4, 1, sharex=True, figsize=(20, 11.25)
    # )
    # ax[0].scatter(
    #     pa0215.dataset.Epoch, pa0215.dataset.ODI_Position[:, 0].where(pa0215.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[0].set_ylabel("X1 (km)")
    # ax[1].scatter(
    #     pa0215.dataset.Epoch, pa0215.dataset.ODI_Position[:, 1].where(pa0215.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[1].set_ylabel("X2 (km)")
    # ax[2].scatter(
    #     pa0215.dataset.Epoch, pa0215.dataset.ODI_Position[:, 2].where(pa0215.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[2].set_ylabel("X3 (km)")
    # ax[3].scatter(
    #     pa0215.dataset.Epoch, pa0215.dataset.ODI_unilib_L_star[:].where(pa0215.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[3].set_xlabel("Time")
    # ax[3].set_ylabel("Lstar")
    # ax[3].set_xlim(datetime.datetime(2024, 1, 2), datetime.datetime(2024, 1, 10))
    # plt.show()
    #
    # fig, ax = plt.subplots(
    #     4, 1, sharex=True, figsize=(20, 11.25)
    # )
    # ax[0].scatter(
    #     pa0207.dataset.Epoch, pa0207.dataset.ODI_Position[:, 0].where(pa0207.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[0].set_ylabel("X1 (km)")
    # ax[1].scatter(
    #     pa0207.dataset.Epoch, pa0207.dataset.ODI_Position[:, 1].where(pa0207.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[1].set_ylabel("X2 (km)")
    # ax[2].scatter(
    #     pa0207.dataset.Epoch, pa0207.dataset.ODI_Position[:, 2].where(pa0207.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[2].set_ylabel("X3 (km)")
    # ax[3].scatter(
    #     pa0207.dataset.Epoch, pa0207.dataset.ODI_unilib_L_star[:].where(pa0207.dataset.ODI_unilib_L_star > 0)
    # )
    # ax[3].set_xlabel("Time")
    # ax[3].set_ylabel("Lstar")
    #
    # ax[3].set_xlim(datetime.datetime(2024, 1, 2), datetime.datetime(2024, 1, 10))
    # plt.show()
    # Make contour plots
    #  plotContour(
    #      pa0207, pa0215, omniDs, energiesToPlot, currentDir, startDatList[i], endDatList[i], monthlyOrYearly
    #  )

    # Make flux vs. time plot
    # plotFluxTS(
    #     pa0207, pa0215, omniDs, energiesToPlot, currentDir, startDatList[i], endDatList[i], monthlyOrYearly
    # )