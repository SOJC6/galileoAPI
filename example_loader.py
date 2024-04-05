# Example loader code for ARASE HEP instrument L3 data
from typing import Union, List

import dateutil.parser
import numpy as np
from spacepy import pycdf

class variable:

    def __init__(self, name, key, description, constant = False):
        self.name = name
        self.key = key
        self.description = description
        self.constant = constant

class product:

    def __init__(self, name, key, level, instrument, satellite, description, filefmt, monthdir, variables):
        self.name = name
        self.key = key
        self.level = level
        self.instrument = instrument
        self.satellite = satellite
        self.description = description
        self.filefmt = filefmt
        self.monthdir = monthdir
        self.variables = variables

    def filename(self, date):
        base_dir = "/data/spacecast/satellite/RBSP/data/rbspa"
        # If the directory structure breaks files up into dates, we need to ensure that we include these. The
        # following will be a blank string if this particular dataproduct doesn't have month-level directories
        monthstr = f"{date.month:02}/" if self.monthdir else ""
        # RBSP data has directories like "level2/sectors". The self.key variable contains these values if there is
        # any such subdirectory structure, otherwise it's blank
        subdir = f"{self.key}/" if self.key else ""
        # Usually there will be level structure to the data (i.e., level2, level3). Sometimes there won't be,
        # however. If there isn't, this will be blank
        level = f"{self.level}/" if self.level else ""
        dir = f"{base_dir}/{self.instrument}/{level}{subdir}{date.year}/{monthstr}"
        # I use %%DATE%% as a placeholder for the date, and then just replace it when it comes time to generate the
        # filename
        return f"{dir}{self.filefmt.replace('%%DATE%%', date.strftime('%Y%m%d'))}"

    def _load(self, date, variables = None):
        # I split the actual data loading off into a separate function, which makes it easier to load ranges of dates

        # Create the filename to load
        fname = self.filename(date)
        data = {}
        # Replace this with CDFLib equivalent
        cdf = pycdf.CDF(fname)
        # If no list of variables was passed in to load, just load all of them
        if not variables:
            variables = self.variables.keys()
        # Iterate through the list of
        for var in variables:
            # I make sure all my variable names are in lowercase, as it makes it easier
            varl = var.lower()
            if varl not in self.variables.keys():
                raise RuntimeError(f"'{var}' is not a variable in the {self.name} data product")
            # I use the variable.key value as the actual name of the variable in the file (i.e., with the correct case)
            data[varl] = pycdf.CDF[self.variables[varl].key()]
        return data

    def load(self, dates: Union[str, List[str]], variables = None, collate = True):
        # I tend to pass my dates in as datestrings, but you can replace this with datetime objects instead easily
        # enough

        # If we haven't been passed a list, we only need to load a single days data
        if not isinstance(dates, str):
            return self._load(dateutil.parser.parse(dates), variables)

        ds = []
        for d in dates:
            # Load the data for each date
            ds.append(self._load(d, variables))

        # This will be different if you're using xarrays
        if collate:
            # If requested, collate the data into a single dictionary
            for key, value in ds[0]:
                # concatenate all of the variables of the same name into a single dictionary value
                ds[0][key] = np.concatenate([data[key] for data in ds])
            # Remove the other dictionaries -- we don't need them any more
            ds = ds[0]
        return ds

pa = product(
    name='Pitch-angle resolved high-energy electron data (Low)',
    key='pa',
    level="l3",
    instrument='hep',
    satellite='arase',
    description='Pitch-angle resolved electron data, binned by energy',
    filefmt=('erg_hep_l3_pa_%%DATE%%_v01_01.cdf',),
    monthdir=True,
    variables={
        'epoch_l': variable(
            name='Time label in the CDF_TT2000 format for HEP-L (the start time of each spin)',
            key='Epoch_L',
            description='Time label in the CDF_TT2000 format for HEP-L (the start time of each spin)',
        ),
        'fedu_l': variable(
            name='Uni-directional differential number flux for HEP-L sorted by pitch angle',
            key='FEDU_L',
            description='Uni-directional differential number flux for HEP-L sorted by pitch angle',
        ),
        'fedu_l_energy': variable(
            name='Energy bin boundaries for HEP-L',
            key='FEDU_L_Energy',
            description='Energy bin boundaries for HEP-L',
            constant=True
        ),
        'fedu_l_alpha': variable(
            name='Central angles of pitch angle bins for HEP-L',
            key='FEDU_L_Alpha',
            description='Central angles of pitch angle bins for HEP-L',
            constant=True
        ),
        'fedu_l_alpha_bin': variable(
            name='Upper/lower boundaries of pitch angle bins for HEP-L',
            key='FEDU_L_Alpha_bin',
            description='Upper/lower boundaries of pitch angle bins for HEP-L',
            constant=True
        ),
        'epoch_h': variable(
            name='Time label in the CDF_TT2000 format for HEP-H (the start time of each spin)',
            key='Epoch_H',
            description='Time label in the CDF_TT2000 format for HEP-H (the start time of each spin)',
        ),
        'fedu_h': variable(
            name='Uni-directional differential number flux for HEP-H sorted by pitch angle',
            key='FEDU_H',
            description='Uni-directional differential number flux for HEP-H sorted by pitch angle',
        ),
        'fedu_h_energy': variable(
            name='Energy bin boundaries for HEP-H',
            key='FEDU_H_Energy',
            description='Energy bin boundaries for HEP-H',
            constant=True
        ),
        'fedu_h_alpha': variable(
            name='Central angles of pitch angle bins for HEP-H',
            key='FEDU_H_Alpha',
            description='Central angles of pitch angle bins for HEP-H',
            constant=True
        ),
        'fedu_h_alpha_bin': variable(
            name='Upper/lower boundaries of pitch angle bins for HEP-H',
            key='FEDU_H_Alpha_bin',
            description='Upper/lower boundaries of pitch angle bins for HEP-H',
            constant=True
        ),
    }
)

