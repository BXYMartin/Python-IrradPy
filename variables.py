# The esdt_dir can be looked up at
# https://goldsmr4.gesdisc.eosdis.nasa.gov/data/
# https://goldsmr5.sci.gsfc.nasa.gov/data/

var_list = {
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
