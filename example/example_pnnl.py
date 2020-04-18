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
    lats = np.array([[10, 0]])
    lons = np.array([[20, 10]])
    # timedef is a list of pandas time series definition for each location defined.
    # Note that an individual time series can be specified per site
    timedef = [pd.date_range(start='2015-06-14T20:00:00', end='2015-06-14T21:00:00', freq='60T'), pd.date_range(start='2015-06-15T20:00:00', end='2015-06-15T21:00:00', freq='60T')]

    time = irradpy.model.timeseries_builder(timedef, np.size(lats))
    # extract the variable from the dataset
    print(time)
    PNNLdata = irradpy.extractor.extract_for_PNNL(lats, lons, time, data_dir)

    # Save the data to file
    for i in range(len(time)):
        # ['par_diffuse', 'par_direct', 'sw_diffuse', 'sw_direct', 'quality_flag']
        print("Time - " + str(time[i][0]) + " -> " + str(time[i][-1]))
        # Build Example
        example = "\texample: [["
        for lon in lons[0]:
            for lat in lats[0]:
                example += str([(lat, lon, str(hr[0])) for hr in time[i]]) + " "
        example = example[0:-1]
        example += "]]"
        print(example.replace(",", ""))
        for item in ['par_diffuse', 'par_direct', 'sw_diffuse', 'sw_direct', 'quality_flag']:
            # PNNLdata[i][item] is DataArray, each item corresponding to the time sequence (1 hr)
            print("\t" + item + ": " + str(PNNLdata[i][item].values).replace("\n", ""))
            np.save(item + ".npy", PNNLdata[i][item])

