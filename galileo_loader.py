import numpy as np
import datetime
from cdflib import xarray as cxr
import xarray as xr
import os
import json
import sys
import requests
import keyring
import pysftp
from skyfield.api import load, wgs84, EarthSatellite, utc

sys.path.append("/Users/matlang/PycharmProjects/datetimeConv/")
import conversions as dtConv

sys.path.append("/Users/matlang/IRBEM/python/IRBEM/")
from readTLE import runIRBEM

import matplotlib.pyplot as plt

class variable:
    def __init__(
            self, key, name
    ):
        self.key = key
        self.name = name

class product:
    def __init__(
            self, name, description,
            instrument, satellite, level, version,
            variables, dataset, irbemCoords=False
    ):
        self.name = name
        self.description = description
        self.instrument = instrument
        self.satellite = satellite
        self.level = level
        self.version = version
        self.variables = variables
        self.dataset = dataset
        self.irbemCoords = irbemCoords

    def fileName(self, date):
        # Define the filename of the data to access for a given date
        # date : datetime
        #  Date to retrieve data for

        rootDir = os.path.abspath(os.path.join(os.sep))
        baseDir = os.path.join(rootDir, 'Users', 'matlang', 'PycharmProjects', 'galileoDataDownload')

        # Extract year, month and day number (as strings) from date
        yearReq = date.strftime("%Y")
        monthReq = date.strftime("%m")
        dayReq = date.strftime("%d")

        instr = f"{self.instrument}"
        sat = f"{self.satellite}"
        levReq = f"l{self.level}"
        verReq = f"V{self.version:02d}"

        # Generate string representing folder containing observations
        #  (also base of file name)
        satFolder = f"galileo_gssc_{instr}_{sat}_sd_{levReq}"

        # File directory path
        fileDir = os.path.join(baseDir, sat, yearReq)
        fName = f"{satFolder}_{yearReq}{monthReq}{dayReq}_{verReq}.cdf"

        outFilePath = f"{os.path.join(fileDir, fName)}"

        return outFilePath


    def fileNameBS(self, date):
        # Define the filename of the data to access for a given date
        # date : datetime
        #  Date to retrieve data for

        rootDir = os.path.abspath(os.path.join(os.sep))
        baseDir = os.path.join(rootDir, 'data', 'spacecast', 'galileo')

        # Extract year, month and day number (as strings) from date
        yearReq = date.strftime("%Y")
        monthReq = date.strftime("%m")
        dayReq = date.strftime("%d")

        instr = f"{self.instrument}"
        sat = f"{self.satellite}"
        levReq = f"l{self.level}"
        verReq = f"V{self.version:02}"

        # Generate string representing folder containing observations
        #  (also base of file name)
        satFolder = f"galileo_gssc_{instr}_{sat}_sd_{levReq}"

        # File directory path
        fileDir = os.path.join(baseDir, instr, satFolder, yearReq)
        fName = f"{satFolder}_{yearReq}{monthReq}{dayReq}_{verReq}.cdf"

        outFilePath = f"{os.path.join(fileDir, fName)}"

        return outFilePath

    def _load(self, date, variables = None):
        # Split the actual data loading off into a separate function, which makes it easier to load ranges of dates
        fname = self.fileName(date)

        if os.path.isfile(fname):
            # Read in cdf file and convert to xarray
            ds = cxr.cdf_to_xarray(fname, to_datetime=True)

            # If variables isn't defined, return the entire dataset
            if not variables:
                variables = self.variables.keys()

            # Remove fill values
            for var in variables:
                # Check if var requested is contained within ds.variables, if not, skip.
                if var not in ds.variables:
                    print(f"Variable {var} requested is not in {fname}. Skipping...")
                else:
                    # If data type of 'var' is 'data' replace the fill val with np.nan
                    if ds[var].attrs['VAR_TYPE'] == 'data':
                        ds[var] = ds[var].where(ds[var] != ds[var].attrs['FILLVAL'])


            # Delete variables not in variables list
            varToDel = [var for var in ds.variables if var not in variables]
            ds = ds.drop_vars(varToDel)

            return ds
        else:
            print(f"File {fname} does not exist. Skipping...")

            return False


    def _loadBS(self, date, variables = None):
        # Split the actual data loading off into a separate function, which makes it easier to load ranges of dates
        fname = self.fileNameBS(date)

        fileName = fname.split(os.sep)[-1]
        print(fileName)

        # Find current directory
        currentDir = os.path.dirname(os.path.abspath(__file__))

        # Make output directory if it doesn't already exist
        tempDir = os.path.join(currentDir, "temp")
        if not os.path.isdir(tempDir):
            os.makedirs(tempDir)

        with open(os.path.join(currentDir, "config.json"), 'r') as fd:
            data_dict = json.load(fd)

        if not os.path.isfile(f"{os.path.join(tempDir, fname)}"):
            try:
                with pysftp.Connection(
                        host=data_dict["host"], username=data_dict["user"],
                        password=keyring.get_password(data_dict["password_hash"], data_dict["user"])
                ) as sftp:
                    print(sftp.isfile(fname))
                    if sftp.isfile(fname):
                        sftp.get(fname, os.path.join(tempDir, fileName))
                    else:
                        print(f"File {fname} does not exist. Skipping...")

                        return False
            except:
                print("Memory allocation error. Skipping...")

        # Read in cdf file and convert to xarray
        ds = cxr.cdf_to_xarray(os.path.join(tempDir, fileName), to_datetime=True)

        # If variables isn't defined, return the entire dataset
        if not variables:
            variables = self.variables.keys()

        # Remove fill values
        for var in variables:
            # Check if var requested is contained within ds.variables, if not raise an exception.
            if var not in ds.variables:
                print(f"Variable {var} requested is not in {fname}. Skipping...")
            else:
                # If data type of 'var' is 'data' replace the fill val with np.nan
                if ds[var].attrs['VAR_TYPE'] == 'data':
                    ds[var] = ds[var].where(ds[var] != ds[var].attrs['FILLVAL'])

        # Delete variables not in variables list
        varToDel = [var for var in ds.variables if var not in variables]
        ds = ds.drop_vars(varToDel)

        return ds


    def _loadHPC(self, date, variables = None):
        # Split the actual data loading off into a separate function, which makes it easier to load ranges of dates
        fname = self.fileNameBS(date)

        fileName = fname.split(os.sep)[-1]
        print(fileName)

        # Read in cdf file and convert to xarray
        if os.path.isfile(f"{fname}"):
            try:
                # Read in cdf file and convert to xarray
                ds = cxr.cdf_to_xarray(fname, to_datetime=True)
            except:
                print(f"File {fname} cannot be converted to xarray. Skipping...")
                return False
        else:
            print(f"File {fname} does not exist. Skipping...")
            return False

        # If variables isn't defined, return the entire dataset
        if not variables:
            variables = self.variables.keys()

        # Remove fill values
        for var in variables:
            # Check if var requested is contained within ds.variables, if not raise an exception.
            if var not in ds.variables:
                print(f"Variable {var} requested is not in {fname}. Skipping...")
            else:
                # If data type of 'var' is 'data' replace the fill val with np.nan
                if ds[var].attrs['VAR_TYPE'] == 'data':
                    ds[var] = ds[var].where(ds[var] != ds[var].attrs['FILLVAL'])

        # Delete variables not in variables list
        varToDel = [var for var in ds.variables if var not in variables]
        ds = ds.drop_vars(varToDel)

        return ds

    def _loadBS(self, date, variables = None):
        # Split the actual data loading off into a separate function, which makes it easier to load ranges of dates
        fname = self.fileNameBS(date)

        fileName = fname.split(os.sep)[-1]
        print(fileName)

        # Find current directory
        currentDir = os.path.dirname(os.path.abspath(__file__))

        # Make output directory if it doesn't already exist
        tempDir = os.path.join(currentDir, "temp")
        if not os.path.isdir(tempDir):
            os.makedirs(tempDir)

        with open(os.path.join(currentDir, "config.json"), 'r') as fd:
            data_dict = json.load(fd)

        if not os.path.isfile(f"{os.path.join(tempDir, fname)}"):
            try:
                with pysftp.Connection(
                        host=data_dict["host"], username=data_dict["user"],
                        password=keyring.get_password(data_dict["password_hash"], data_dict["user"])
                ) as sftp:
                    print(sftp.isfile(fname))
                    if sftp.isfile(fname):
                        sftp.get(fname, os.path.join(tempDir, fileName))
                    else:
                        print(f"File {fname} does not exist. Skipping...")

                        return False
            except:
                print("Memory allocation error. Skipping...")

        # Read in cdf file and convert to xarray
        ds = cxr.cdf_to_xarray(os.path.join(tempDir, fileName), to_datetime=True)

        # If variables isn't defined, return the entire dataset
        if not variables:
            variables = self.variables.keys()

        # Remove fill values
        for var in variables:
            # Check if var requested is contained within ds.variables, if not raise an exception.
            if var not in ds.variables:
                print(f"Variable {var} requested is not in {fname}. Skipping...")
            else:
                # If data type of 'var' is 'data' replace the fill val with np.nan
                if ds[var].attrs['VAR_TYPE'] == 'data':
                    ds[var] = ds[var].where(ds[var] != ds[var].attrs['FILLVAL'])

        # Delete variables not in variables list
        varToDel = [var for var in ds.variables if var not in variables]
        ds = ds.drop_vars(varToDel)

        return ds


    def load(self, dates, variables=None):

        # If dates is a single datetime value, then just return a single timestep
        if type(dates) == 'datetime':
            dsOut = self._load(dates, variables)

            return dsOut

        #Otherwise, concatenate all required dates together
        dsOut = False
        for d, dat in enumerate(dates):
            if not dsOut:
                dsOut = self._load(dat, variables)
            else:
                ds2 = self._load(dat, variables)

                # Check ds2 returns a non-false value
                if ds2:
                    dsOut = xr.concat([dsOut, ds2], dim="Epoch")


        self.dataset = dsOut

    def loadBS(self, dates, variables=None):
        # If dates is a single datetime value, then just return a single timestep
        if type(dates) == 'datetime':
            if use_hpc:
                dsOut = self._loadHPC(dates, variables)
            else:
                dsOut = self._loadBS(dates, variables)

            return dsOut
        print(variables)

        # Otherwise, concatenate all required dates together
        dsOut = False
        for d, dat in enumerate(dates):
            if not dsOut:
                if use_hpc:
                    dsOut = self._loadHPC(dat, variables)
                else:
                    dsOut = self._loadBS(dat, variables)
            else:
                if use_hpc:
                    ds2 = self._loadHPC(dat, variables)
                else:
                    ds2 = self._loadBS(dat, variables)

                # Check ds2 returns a non-false value
                if ds2:
                    dsOut = xr.concat([dsOut, ds2], dim="Epoch")

        print(ds2)

        # If irbemCoords=True, use IRBEM to generate Lstar values in ds
        if self.irbemCoords:
            if self.satellite.lower() == "gsat0207":
                satReq = 41859
            elif self.satellite.lower() == "gsat0215":
                satReq = 43055
            else:
                print("Defaulting to GSAT0207")
                satReq = 41859

            timeSeries64 = dsOut.Epoch
            print(f"ts64={timeSeries64}")

            ts = load.timescale()
            timeSeriesTs = np.array([
                dtConv.dt64ToTimestamp(t) for t in timeSeries64.values
            ])

            # Define IRBEM options
            irbemOpt1 = 1
            irbemOpt2 = 0
            irbemOpt3 = 0
            irbemOpt4 = 0
            irbemOpt5 = 0

            # Define kextField
            kextField = "OPQ77"
            print(f"opt3={irbemOpt3}, opt4={irbemOpt4}")
            ds3 = runIRBEM(
                satReq, ts, timeSeriesTs,
                opt1=irbemOpt1, opt2=irbemOpt2, opt3=irbemOpt3,
                opt4=irbemOpt4, opt5=irbemOpt5, kextField=kextField,
                fileOMNI="", defOrRTkp="rt"
            )
            dsOut = xr.merge([dsOut, ds3])

        if dsOut:
            # Find current directory
            currentDir = os.path.dirname(os.path.abspath(__file__))
            # fig, ax = plt.subplots(1, 1, figsize=(20, 11.25))
            # ax.plot(dsOut.Epoch, dsOut.ODI_unilib_L_star.where(dsOut.ODI_unilib_L_star>0))
            # ax.set_ylabel("ODI_unilib_L_star")
            # ax.set_xlabel("Time")
            # ax.set_title("Calculated L_star within Galileo cdf file against time")
            # plt.savefig(f"{currentDir}/plots0207/{dates[0].strftime('%Y-%m')}_Lstar.png")
            self.dataset = dsOut
        #return dsOut

