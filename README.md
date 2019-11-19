# Python-MERRA2
Python script to download data from gesdisc.eosdis.nasa.gov

## Functions
* Skip already downloaded files.
* Automatically merge files by year.
* Allow multi-field selection for each table.

## Usage
### Setup authentication
``` bash
cd ~
touch .netrc         # Create File
chmod 0600 .netrc    # Fix Permission
echo "machine urs.earthdata.nasa.gov login USERNAME password PASSWORD" >> .netrc
                     # Save Authentication
touch .urs_cookies
```

### Project structure
|   File Name   |            Purpose             |
| :-----------: | :----------------------------: |
| `download.py` |      main download logic       |
| `variable.py` | define download urls and paths |
|   `test.py`   |       run download tests       |

### Directory
```
.
├── download.py
├── resources
│   ├── index.npy (log download status)
│   ├── FIELD_day_merra2_reanalysis_2015.nc4 (storage data for specific FIELD)
├── test.py
└── variables.py
```
### Run
``` bash
cd PROJECT_DIRECTORY
python test.py
```
