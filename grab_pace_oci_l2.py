import numpy as np
import numpy as np
import xarray as xr
from netCDF4 import Dataset

def load_oci_l2(fn, full_flag = True):
    # create the initial dataset so that we have all the attributes
    xds = xr.open_dataset(fn)
    # open the file with netCDF to get all the actual data
    dataset = Dataset(fn)
    
    # grab the necessary group data
    gd    = dataset.groups['geophysical_data']
    nav   = dataset.groups['navigation_data']
    lons  = nav.variables["longitude"][:]
    lats  = nav.variables["latitude"][:]
    flags = gd.variables["l2_flags"][:]
    wls = dataset.groups['sensor_band_parameters']['wavelength_3d'][:].data

    # create the dataset, now we're only adding in Rrs
    # but the options are: ['Rrs', 'Rrs_unc', 'aot_865', 'angstrom', 'avw', 'l2_flags']
    rrs_xds = xr.Dataset({'Rrs':(('x', 'y', 'wl'),gd.variables['Rrs'][:].data)},
                        coords = {'latitude': (('x', 'y'), lats),
                                  'longitude': (('x', 'y'), lons),
                                  'wavelength' : ('wl', wls)},
                        attrs={'variable':'Remote sensing reflectance'})
    
    # merge back into the xarray dataset with all the attributes
    xds['Rrs'] = rrs_xds.Rrs
    # replace nodata areas with nan
    xds = xds.where(xds['Rrs'] != -32767.0)

    # eliminate everything that isn't a flag bit of 0 (meaning no flags)
    if full_flag:
        xds['Rrs'] = xr.where(xr.DataArray(flags.data, dims=['x', 'y'])==0, xds['Rrs'], np.nan)
        
    return(xds)
