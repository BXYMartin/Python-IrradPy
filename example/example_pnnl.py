import numpy as np
import irradpy
import os
import datetime
import pandas as pd

if __name__ == '__main__':
    # Merge All Files
    # You should put all files under a folder named PNNL_data along with this script
    data_dir = os.path.join(os.getcwd(), "PNNL_data")
    # You should put all the *.nc files into the root of the PNNL_data folder
    irradpy.downloader.pnnl.run(data_dir=data_dir, merge_timelapse="monthly")
    # Define lats and lons of the interest site
    # lat is [0, 179.9], lon is [0, 359.9]
    lats = [10]
    lons = [20]
    # timedef is a list of pandas time series definition for each location defined.
    # Note that an individual time series can be specified per site
    timedef = [pd.date_range(start='2015-06-14T20:00:00', end='2015-06-14T21:00:00', freq='60T')]

    time = irradpy.model.timeseries_builder(timedef, np.size(timedef))
    # extract the variable from the dataset
    PNNLdata = irradpy.extractor.extract_for_PNNL(lats, lons, time, data_dir)

    # Save the data to file
    for i in range(len(timedef)):
        # ['par_diffuse', 'par_direct', 'sw_diffuse', 'sw_direct', 'quality_flag']
        for item in ['par_diffuse', 'par_direct', 'sw_diffuse', 'sw_direct', 'quality_flag']:
            # PNNLdata[i][item] is DataArray, each item corresponding to the time sequence (1 hr)
            print(item + ": " + str(PNNLdata[i][item].values).replace("\n", ""))
            np.save(item + ".npy", PNNLdata[i][item])

