# The esdt_dir can be looked up at
# https://goldsmr4.gesdisc.eosdis.nasa.gov/data/
# https://goldsmr5.sci.gsfc.nasa.gov/data/

var_list = {
    "tasmax": {
        "esdt_dir": "M2SDNXSLV.5.12.4",
        "collection": "statD_2d_slv_Nx",
        "merra_name": ["T2MMAX", "T2MMIN"],
        "standard_name": "air_temperature",
        "least_significant_digit": 3,
    },
    "tasmin": {
        "esdt_dir": "M2SDNXSLV.5.12.4",
        "collection": "statD_2d_slv_Nx",
        "merra_name": "T2MMIN",
        "standard_name": "air_temperature",
        "least_significant_digit": 3,
    },
    "uas": {
        "esdt_dir": "M2I1NXASM.5.12.4",
        "collection": "inst1_2d_asm_Nx",
        "merra_name": "U10M",
        "standard_name": "eastward_wind",
        "least_significant_digit": 3,
    },
    "vas": {
        "esdt_dir": "M2I1NXASM.5.12.4",
        "collection": "inst1_2d_asm_Nx",
        "merra_name": "V10M",
        "standard_name": "northward_wind",
        "least_significant_digit": 3,
    },
    "rad": {
        "esdt_dir": "M2T1NXRAD.5.12.4",
        "collection": "tavg1_2d_rad_Nx",
        "merra_name": "ALBEDO",
        "standard_name": "radiation",
    },
    "slv": {
        "esdt_dir": "M2T1NXSLV.5.12.4",
        "collection": "tavg1_2d_slv_Nx",
        "merra_name": ["TQV", "TO3", "PS"],
        "standard_name": "surface",
        "least_significant_digit": 3,
    },
    "aer": {
        "esdt_dir": "M2T1NXAER.5.12.4",
        "collection": "tavg1_2d_aer_Nx",
        "merra_name": ["TOTSCATAU", "TOTEXTTAU", "TOTANGSTR"],
        "standard_name": "aerosols",
        "least_significant_digit": 3,
    },
}
