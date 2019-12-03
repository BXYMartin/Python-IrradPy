# ClearSkyPy
Python script to download data from gesdisc.eosdis.nasa.gov for Clear Sky Model.

## Functions
* Skip already downloaded files.
* Automatically merge files by year.
* Allow multi-field selection for each table.
* To Be Continue...

## Details
### Requirements
* Python >= 3.6
### Overview
* Register on GESDISC website and get your authentication.
* Install the script to your computer.
    - You can either download this package from the [Github Release Page](https://github.com/BXYMartin/Python-MERRA2/releases) and [Github Package Page](https://github.com/BXYMartin/Python-MERRA2/packages), or clone this repository and run `python setup.py install`. 
* Run the script.

### Usage
#### Use inside Python Script
``` python
# Linux and Unix Users
import clearskypy
# Run Downloader
clearskypy.downloader.run(auth={"uid":"USERNAME", "password": "PASSWORD"})


# Windows Users Only:
import clearskypy
import multiprocessing
# Important Note: If you're using windows, make sure to wrap the function.
if __name__ == "__main__":
    multiprocessing.freeze_support()
    clearskypy.downloader.run(auth={"uid":"USERNAME", "password": "PASSWORD"})
    
# More Examples
# Download All Data From 2018-01-01 To 2018-01-02
clearskypy.downloader.run(auth={"uid":"USERNAME", "password": "PASSWORD"},
    initial_year=2018, final_year=2018,
    initial_month=1, final_month=1,
    initial_day=1, final_day=2,
    lat_1=-90, lat_2=90,
    lon_1=-180, lon_2=180,
    delete_temp_dir=True, verbose=True,
    thread_num=20, connection_num=2
    )
```

``` python
    Parameters
    
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
    delete_temp_dir : bool
    verbose : bool
    thread_num : Optional[int]
        Number of Files to be downloaded simutanously.
    connection_num : Optional[int]
        Number of Connections for each file to be downloaded simutanously.
```

#### Run Package From Shell
``` bash
python -m clearskypy.downloader.socket --uid USERNAME --password PASSWORD

usage: socket.py [-h] [--collection_names VAR_NAMES] [--delete_temp DELETE_TEMP]
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

usage: merra2_downloader [-h] [--collection_names VAR_NAMES]
                         [--delete_temp DELETE_TEMP]
                         [--download_dir DOWNLOAD_DIR]
                         [--initial_year INITIAL_YEAR]
                         [--initial_month INITIAL_MONTH]
                         [--initial_day INITIAL_DAY] [--final_year FINAL_YEAR]
                         [--final_month FINAL_MONTH] [--final_day FINAL_DAY]
                         --uid UID [--password PASSWORD]
                         [--bottom_left_lat BOTTOM_LEFT_LAT]
                         [--bottom_left_lon BOTTOM_LEFT_LON]
                         [--top_right_lat TOP_RIGHT_LAT]
                         [--top_right_lon TOP_RIGHT_LON]
                         [--thread_num THREAD_NUM]
                         [--connection_num CONNECTION_NUM]
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
Still working on it...

#### To Be Continue...

### Directory
#### Package
```
.
├── MERRA2_CSM
│   ├── __init__.py
│   └── downloader
│       ├── __init__.py
│       ├── download.py
│       ├── process.py
│       ├── socket.py
│       └── variables.py
├── README.md
└── setup.py
```
#### Download Directory
```
.
└─ MERRA2_data
   ├── index.npy                            // logs for downloaded files
   ├── xxx_xxx_merra2_reanalysis_xxxx.nc    // merged file
   └── tmpxxxxxxxx                          // temp directory
       └── MERRA2_400.xxx.xxx.nc4.nc        // original files
```
### Install
With source code:
``` bash
python setup.py install
```
With python package:
``` bash
pip install xxx
```
