# The esdt_dir can be looked up at
# https://goldsmr4.gesdisc.eosdis.nasa.gov/data/
# https://goldsmr5.sci.gsfc.nasa.gov/data/


var_list = {
        "rad": {
            "esdt_dir": "M2T1NXRAD.5.12.4",
            "collection": "tavg1_2d_rad_Nx",
            "var_name": ["ALBEDO", "CLDTOT", "SWGDN", "SWGDNCLR", "TAUTOT"],
            "standard_name": "radiation",
        },
        "slv": {
            "esdt_dir": "M2T1NXSLV.5.12.4",
            "collection": "tavg1_2d_slv_Nx",
            "var_name": ["TQV", "TO3", "PS"],
            "standard_name": "surface",
        },
        "aer": {
            "esdt_dir": "M2T1NXAER.5.12.4",
            "collection": "tavg1_2d_aer_Nx",
            "var_name": ["TOTSCATAU", "TOTEXTTAU", "TOTANGSTR"],
            "standard_name": "aerosols",
        },
        "asm": {
            "esdt_dir": "M2C0NXASM.5.12.4",
            "collection": "const_2d_asm_Nx",
            "var_name": ["PHIS"],
            "standard_name": "parameters",
        },
        "dewpt": {
            "esdt_dir": "M2T1NXSLV.5.12.4",
            "collection": "tavg1_2d_slv_Nx",
            "var_name": ["T2MDEW"],
            "standard_name": "dew_point_temperature",
        },
        "evspsbl": {
            "esdt_dir": "M2T1NXFLX.5.12.4",
            "collection": "tavg1_2d_flx_Nx",
            "var_name": ["EVAP"],
            "standard_name": "water_evaporation_flux",
        },
        "hur": {
            "esdt_dir": "M2T3NPCLD.5.12.4",
            "collection": "tavg3_3d_cld_Np",
            "var_name": ["RH"],
            "standard_name": "relative_humidity",
        },
        "huss": {
            "esdt_dir": "M2T1NXSLV.5.12.4",
            "collection": "tavg1_2d_slv_Nx",
            "var_name": ["QV2M"],
            "standard_name": "specific_humidity",
        },
        "phis": {
            "esdt_dir": "M2C0NXASM.5.12.4",
            "collection": "const_2d_asm_Nx",
            "var_name": ["PHIS"],
            "standard_name": "surface_geopotential",
        },
        "pr": {
            "esdt_dir": "M2T1NXFLX.5.12.4",
            "collection": "tavg1_2d_flx_Nx",
            "var_name": ["PRECTOT"],
            "standard_name": "precipitation_flux",
        },
        "prc": {
            "esdt_dir": "M2T1NXFLX.5.12.4",
            "collection": "tavg1_2d_flx_Nx",
            "var_name": ["PRECCON"],
            "standard_name": "convective_precipitation_flux",
        },
        "prbc": {
            "esdt_dir": "M2T1NXFLX.5.12.4",
            "collection": "tavg1_2d_flx_Nx",
            "var_name": ["PRECTOTCORR"],
            "standard_name": "precipitation_flux_bias_corr",
        },
        "prmax": {
            "esdt_dir": "M2SDNXSLV.5.12.4",
            "collection": "statD_2d_slv_Nx",
            "var_name": ["TPRECMAX"],
            "standard_name": "precipitation_flux",
        },
        "prsn": {
            "esdt_dir": "M2T1NXFLX.5.12.4",
            "collection": "tavg1_2d_flx_Nx",
            "var_name": ["PRECSNO"],
            "standard_name": "snowfall_flux",
        },
        "rls": {
            "esdt_dir": "M2T1NXRAD.5.12.4",
            "collection": "tavg1_2d_rad_Nx",
            "var_name": ["LWGNT"],
            "standard_name": "surface_net_downward_longwave_flux",
        },
        "sftgif": {
            "esdt_dir": "M2C0NXASM.5.12.4",
            "collection": "const_2d_asm_Nx",
            "var_name": ["FRLANDICE"],
            "standard_name": "land_ice_area_fraction",
        },
        "sftkf": {
            "esdt_dir": "M2C0NXASM.5.12.4",
            "collection": "const_2d_asm_Nx",
            "var_name": ["FRLAKE"],
            "standard_name": "lake_area_fraction",
        },
        "sftlf": {
            "esdt_dir": "M2C0NXASM.5.12.4",
            "collection": "const_2d_asm_Nx",
            "var_name": ["FRLAND"],
            "standard_name": "land_area_fraction",
        },
        "sftof": {
            "esdt_dir": "M2C0NXASM.5.12.4",
            "collection": "const_2d_asm_Nx",
            "var_name": ["FROCEAN"],
            "standard_name": "sea_area_fraction",
        },
        "shg": {
            "esdt_dir": "M2C0NXASM.5.12.4",
            "collection": "const_2d_asm_Nx",
            "var_name": ["SHG"],
            "standard_name": "isotropic_stdv_of_gravity_wave_drag_topography",
        },
        "sic": {
            "esdt_dir": "M2T1NXOCN.5.12.4",
            "collection": "tavg1_2d_ocn_Nx",
            "var_name": ["FRSEAICE"],
            "standard_name": "sea_ice_area_fraction",
        },
        "tas": {
            "esdt_dir": "M2T1NXSLV.5.12.4",
            "collection": "tavg1_2d_slv_Nx",
            "var_name": ["T2M"],
            "standard_name": "air_temperature",
        },
        "tasmax": {
            "esdt_dir": "M2SDNXSLV.5.12.4",
            "collection": "statD_2d_slv_Nx",
            "var_name": ["T2MMAX"],
            "standard_name": "air_temperature",
        },
        "tasmin": {
            "esdt_dir": "M2SDNXSLV.5.12.4",
            "collection": "statD_2d_slv_Nx",
            "var_name": ["T2MMIN"],
            "standard_name": "air_temperature",
        },
        "uas": {
            "esdt_dir": "M2I1NXASM.5.12.4",
            "collection": "inst1_2d_asm_Nx",
            "var_name": ["U10M"],
            "standard_name": "eastward_wind",
        },
        "vas": {
            "esdt_dir": "M2I1NXASM.5.12.4",
            "collection": "inst1_2d_asm_Nx",
            "var_name": ["V10M"],
            "standard_name": "northward_wind",
        },
}

