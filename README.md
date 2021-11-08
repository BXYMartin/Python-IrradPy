# IrradPy
[![Build Status](https://travis-ci.org/BXYMartin/Python-irradpy.svg?branch=master)](https://travis-ci.org/BXYMartin/Python-irradpy)
[![Latest Version](https://img.shields.io/github/v/release/bxymartin/python-irradpy)](https://test.pypi.org/project/irradpy/)

Python package to download data from gesdisc.eosdis.nasa.gov for Clear Sky Model, extract variables from the MERRA-2 reanalysis database and model of clear-sky irradiance.

## Example Figure
Using this tool, you can map out the global horizontal irradiance on a global basis or for a specific country. 
Figures below are the output for 1st, January, 2018 to 2nd, January, 2018. Code is available at [Python-IrradPy_Visualization](https://github.com/BXYMartin/Python-IrradPy_Visualization).
![Ortho Image](https://raw.githubusercontent.com/BXYMartin/Python-IrradPy_Visualization/master/figure/ortho_irradiance.png)

![Country Image](https://raw.githubusercontent.com/BXYMartin/Python-IrradPy_Visualization/master/figure/china_irradiance.png)


## Functions
* Skip already downloaded files.
* Automatically merge files by year.
* Allow multi-field selection for each table.
* Extract variables for a given time period from multiple MERRA-2 reanalysis databases.
* Automatic zenith angle calculation.
* Support two models: MAC2 and REST2 models.
* To Be Continue...

## Details
### Requirements
* Python >= 3.6
### Overview
* Register on GESDISC website and get your authentication.
* Install the script to your computer.
    - You can either download this package from the [Github Release Page](https://github.com/BXYMartin/Python-MERRA2/releases) and [Github Package Page](https://github.com/BXYMartin/Python-MERRA2/packages), or clone this repository and run `python setup.py install`. 
* Run the script.

* Download data sets by downloader
* Define latitude, longitude, elevation, time period for a model.
* Run the model.

### Usage
#### Use inside Python Script
``` python
# Linux and Unix Users
import irradpy
# Run Downloader
irradpy.downloader.run(auth={"uid":"USERNAME", "password": "PASSWORD"})
# Run Model
irradpy.model.ClearSkyREST2v5(latitudes, longitudes, elevations, time, dataset_dir).REST2v5()
irradpy.model.ClearSkyMAC2(latitudes, longitudes, elevations, time, dataset_dir).MAC2()


# Windows Users Only:
import irradpy
import multiprocessing
# Important Note: If you're using windows, make sure to wrap the function.
if __name__ == "__main__":
    multiprocessing.freeze_support()
    irradpy.downloader.run(auth={"uid":"USERNAME", "password": "PASSWORD"})
    
# More Examples

# Download All Data From 2018-01-01 To 2018-01-02
irradpy.downloader.run(auth={"uid":"USERNAME", "password": "PASSWORD"},
    initial_year=2018, final_year=2018,
    initial_month=1, final_month=1,
    initial_day=1, final_day=2,
    lat_1=-90, lat_2=90,
    lon_1=-180, lon_2=180,
    verbose=True,
    thread_num=20, connection_num=2
    )

# Run clear sky model from 2018-01-01 To 2018-01-02
time_delta = 10  # minute
timedef = [('2018-01-01T00:00:00', '2018-01-02T0:00:00')]
time = irradpy.model.timeseries_builder(timedef, time_delta, np.size(latitudes))
irradpy.model.ClearSkyREST2v5(latitudes, longitudes, elevations, time, dataset_dir).REST2v5()
```

``` python
    Parameters
    #downloader:
    collection_names : List[str]
        Variable short names, must be defined in variables.py
        if merra2_var_dict is not provided. If more than one variable,
        they are assumed to have the same original files and those will only
        be downloaded once.
    initial_year : int
        Initial year for the data to be downloaded.
        Select from [1980, Now]
    final_year : int
        Final year for the data to be downloaded.
        Select from [1980, Now]
    initial_month : int
        Initial month for the data to be downloaded.
        Select from [1, 12]
    final_month : int
        Final month for the data to be downloaded.
        Select from [1, 12]
    initial_day : int
        Initial day for the data to be downloaded.
        Select from [1, 12]
    final_day : Optional[int]
        Final day for the data to be downloaded.
    lat_1 : Optional[float]
        Define the latitude of the left bottom corner of the rectangle region of interest.
        Select a value from [-90, +90]
    lon_1 : Optional[float]
        Define the longitude of the left bottom corner of the rectangle region of interest.
        Select a value from [-180, +180]
    lat_2 : Optional[float]
        Define the latitude of the right top corner of the rectangle region of interest.
        Select a value from [-90, +90]
    lon_2 : Optional[float]
        Define the longitude of the right top corner of the rectangle region of interest.
        Select a value from [-180, +180]
    merra2_var_dicts : Optional[List[dict]]
        Dictionary containing the following keys:
        esdt_dir, collection, var_name, standard_name,
        see the Bosilovich paper for details. Same order as collection_names.
    output_dir : Union[str, Path]
    auth : dict
        Dictionary contains login information.
        {"uid": "USERNAME", "password": "PASSWORD"}
    verbose : bool
    thread_num : Optional[int]
        Number of Files to be downloaded simutanously.
    connection_num : Optional[int]
        Number of Connections for each file to be downloaded simutanously.
        
    #irradpy.model.timeseries_builder:
    timedef: list [(start time , end time)], optional — specify the start 
        time(s) and end time(s) of the location(s) of interest.
    time_delta: integer, optional — specify the temporal resolution of the 
        time series in minutes
    num_station: integer, compulsory - specify the station number of interest.
        if timedef less than num_station, timeseries_builder will expand it 
        for every station.
    
    #irradpy.model.clearSkyRadiation_MAC2.py && irradpy.model.clearSkyRadiation_REST2v5.py:
    
    latitudes: numpy.ndarray, float, compulsory — Define the latitude(s) of the 
        location(s) of interest, size must match longitudes. 
    longitudes: numpy.ndarray, float, compulsory — Define the longitude(s) of 
        the location(s) of interest, size must match latitudes. 
    elevations: numpy.ndarray, float, compulsory — Define the elevation(s) of 
        the location(s) of interest, size must match lats.
    time: numpy.ndarry of dtype ̄‘datetime64[m]’, compulsory — Define the time 
        series desired.
    dataset_dir: Union[string, Path], optional — Define the location of the 
        dataset of downloaded and merged data.
    
    
```

#### Run Package From Shell
``` bash
python -m irradpy.downloader.socket --uid USERNAME --password PASSWORD

usage: socket.py [-h] [--collection_names VAR_NAMES]
                 [--download_dir DOWNLOAD_DIR] [--initial_year INITIAL_YEAR]
                 [--initial_month INITIAL_MONTH] [--initial_day INITIAL_DAY]
                 [--final_year FINAL_YEAR] [--final_month FINAL_MONTH]
                 [--final_day FINAL_DAY] --uid UID [--password PASSWORD]
                 [--bottom_left_lat BOTTOM_LEFT_LAT]
                 [--bottom_left_lon BOTTOM_LEFT_LON]
                 [--top_right_lat TOP_RIGHT_LAT]
                 [--top_right_lon TOP_RIGHT_LON] [--thread_num THREAD_NUM]
                 [--connection_num CONNECTION_NUM]
```

#### Using Command Line Tools
``` bash
merra2_downloader --uid USERNAME --password PASSWORD

usage: merra2_downloader [-h] --uid UID --password PASSWORD
                         [--collection_names COLLECTION_NAMES]
                         [--download_dir DOWNLOAD_DIR]
                         [--initial_year INITIAL_YEAR]
                         [--initial_month INITIAL_MONTH]
                         [--initial_day INITIAL_DAY] [--final_year FINAL_YEAR]
                         [--final_month FINAL_MONTH] [--final_day FINAL_DAY]
                         [--bottom_left_lat BOTTOM_LEFT_LAT]
                         [--bottom_left_lon BOTTOM_LEFT_LON]
                         [--top_right_lat TOP_RIGHT_LAT]
                         [--top_right_lon TOP_RIGHT_LON]
                         [--thread_num THREAD_NUM]
                         [--connection_num CONNECTION_NUM]
merra2_downloader: the following arguments are required: --uid, --password
```

#### Test Case
``` bash
python setup.py test
```

### Project structure
#### Downloader Module
|   File Name   |            Purpose             |
| :-----------: | :----------------------------: |
| `download.py` |      main download logic       |
| `variable.py` | define download urls and paths |
|   `socket.py`   |    wrapper for downloader   
|   `process.py`|  wrapped download class |

#### Extractor Module
|   File Name   |            Purpose             |
| :-----------: | :----------------------------: |
| `extract.py` |      main extract logic       |

#### Model Module
|   File Name   |            Purpose             |
| :-----------: | :----------------------------: |
| `clearSkyRadiation_MAC2.py.py` |     Clear Sky Model MAC2 Class      |
| `clearSkyRadiation_REST2v5.py.py` | Clear Sky Model REST2 Class  |
| `solarGeometry.py.py`   |    Basic function for clear sky model|   

### Directory
#### Package
```
.
├── irradpy
│   ├── __init__.py
│   ├── downloader
│   │   ├── __init__.py
│   │   ├── download.py
│   │   ├── process.py
│   │   ├── socket.py
│   │   └── variables.py
│   ├── extractor
│   │    ├── __init__.py
│   │    └── extract.py
│   └── model
│        ├── __init__.py
│        ├── clearSkyRadiation_MAC2.py
│        ├── clearSkyRadiation_REST2v5.py
│        └── solarGeometry.py
├── README.md
├── setup.py
├── example
│   ├── example_downloader.py
│   └── example_clearsky.py
└── test
    └── test_downloader.py
```
#### Download Directory
```
.
└─ MERRA2_data
   ├── index.npy                            // logs for downloaded files
   ├── xxx_xxx_merra2_reanalysis_xxxx.nc    // merged file
   └── tmpxxxxxxxx                          // temp directory
       └── MERRA2_nnn.xxx.xxx.nc4.nc        // original files
```
### Install
With source code:
``` bash
python setup.py install
```
With python package:
``` bash
pip install -i https://test.pypi.org/simple/ irradpy
```

## License
This project is licensed under MIT License, feel free to modify or contribute!
