import numpy as np
import clearskypy
import os
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.units as munits
import matplotlib.dates as mdates
import datetime
import pandas as pd

if __name__ == '__main__':
    # check the version for matplotlib for ConciseDateConverter
    assert int(matplotlib.__version__.split('.')[0]) >= 3 and int(matplotlib.__version__.split('.')[1]) >= 1, "Matplotlib >= 3.1 is required for function ConciseDateConverter!"

    # set some example latitudes, longitudes and elevations
    # latitudes range from -90 (south pole) to +90 (north pole) in degrees
    latitudes = np.array([[1.300341, 39.97937]])
    # longitudes range from -180 (west) through 0 at prime meridian to +180 (east)
    longitudes = np.array([[103.771663, 116.34653]])
    # elevations are in metres, this influences some solar elevation angles and scale height corrections
    elevations = np.array([[43, 53]])

    # set the time series that you wish to model. Thi can be unique per locaton.
    # first, specify the temporal resolution in minutes
    # timedef is a list of pandas time series definition for each location defined.

    timedef = [pd.date_range(start='2018-01-01T20:00:00', end='2018-01-02T15:00:00', freq='10T'),
               pd.date_range(start='2018-01-02T20:00:00', end='2018-01-03T15:00:00', freq='10T')]
    # use timeseries_builder to build time series for different station
    time = clearskypy.model.timeseries_builder(timedef, np.size(latitudes))

    # specify where the downloaded dataset is. It is best to use the os.path.join function
    dataset_dir = os.path.join(os.getcwd(), 'MERRA2_data', '2018-1-1~2018-1-3 rad-slv-aer-asm [-90,-180]~[90,180]', '')

    # build the clear-sky REST2v5 model object
    test_rest2 = clearskypy.model.ClearSkyREST2v5(latitudes, longitudes, elevations, time, dataset_dir, pandas=True)
    # run the REST2v5 clear-sky model  output is a list of pandas.Dataframe for each station. col: GHI, DNI, DHI, row: time
    rest2_output = test_rest2.REST2v5()

    # create the MAC2 model class object
    test_mac = clearskypy.model.ClearSkyMAC2(latitudes, longitudes, elevations, time, dataset_dir, pandas=True)
    # run the MAC2 model  output is a list of pandas.Dataframe for each station  col: GHI, DNI, DHI, row: time
    mac2_output = test_mac.MAC2()

    # Create a figure showing the data of both clear-sky estimates
    converter = mdates.ConciseDateConverter()
    munits.registry[np.datetime64] = converter
    munits.registry[datetime.date] = converter
    munits.registry[datetime.datetime] = converter

    plt.style.use('ggplot')
    plt.rcParams["font.family"] = "Times New Roman"
    plt.style.use('ggplot')
    lims = [(time[0][0], time[0][-1]),
            (time[1][0], time[1][-1])]
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3), constrained_layout=True)
    # make the first subplot for the location of SERIS
    t = time[0].astype('O')
    axs[0].plot(t, rest2_output[0].values[:, 0], ls='-', color='blue')
    axs[0].plot(t, rest2_output[0].values[:, 1], ls='--', color='blue')
    axs[0].plot(t, rest2_output[0].values[:, 2], ls='-.', color='blue')
    axs[0].plot(t, mac2_output[0].values[:, 0], ls='-', color='red')
    axs[0].plot(t, mac2_output[0].values[:, 1], ls='--', color='red')
    axs[0].plot(t, mac2_output[0].values[:, 2], ls='-.', color='red')
    axs[0].set_xlim(lims[0])
    plt.sca(axs[0])
    plt.xticks(fontsize=8)
    plt.xlabel('Time UTC')
    plt.ylabel('Irradiance [Wm$^{-2}$]', fontsize=10)
    plt.title('SERIS', fontsize=12, )
    # make the second subplot for the location of Beihang
    t = time[1].astype('O')
    axs[1].plot(t, rest2_output[1].values[:, 0], ls='-', color='blue')
    axs[1].plot(t, rest2_output[1].values[:, 1], ls='--', color='blue')
    axs[1].plot(t, rest2_output[1].values[:, 2], ls='-.', color='blue')
    axs[1].plot(t, mac2_output[1].values[:, 0], ls='-', color='red')
    axs[1].plot(t, mac2_output[1].values[:, 1], ls='--', color='red')
    axs[1].plot(t, mac2_output[1].values[:, 2], ls='-.', color='red')
    axs[1].set_xlim(lims[1])
    axs[1].legend(['GHI REST2', 'DNI REST2', 'DIF REST2', 'GHI MAC2', 'DNI MAC2', 'DIF MAC2'], fontsize=8)
    plt.sca(axs[1])
    plt.xticks(fontsize=8)
    plt.title('Beihang University', fontsize=12)
    plt.xlabel('Time UTC', fontsize=10)
    # save the figure and show to console
    plt.tight_layout()
    fig.savefig('example_image.pdf')
    plt.show()

    # Save the data to file, each site = new file
    for i in range(len(time)):
            savedata = np.array([time[i].flatten(), rest2_output[i].values[:, 0].flatten(), rest2_output[i].values[:, 1].flatten(),
                        rest2_output[i].values[:, 2].flatten(), mac2_output[i].values[:, 0].flatten(), mac2_output[i].values[:, 1].flatten(),
                        mac2_output[i].values[:, 2].flatten()])
            savefname = 'site[' + str(latitudes[0, i]) + ',' + str(longitudes[0, i]) +'].txt'
            np.savetxt(savefname, savedata.T, fmt='%s' + ',%.4f' * 6, delimiter='\n', header='Time, GHIcs REST2, DNIcs REST2, DIFcs REST2, GHIcs MAC2, DNIcs MAC2, DIFcs MAC2')

