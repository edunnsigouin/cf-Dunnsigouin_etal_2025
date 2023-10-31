"""
Performs a spatial (x,y) smoothing on a range of spatial scales
of forecast data and outputs the smoothed forecast fields to file.
"""

import numpy    as np
import xarray   as xr
from forsikring import s2s, verify, misc

# Input -----------------------------------
write2file = False
# -----------------------------------------
