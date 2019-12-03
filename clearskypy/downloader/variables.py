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
            "var_name": ["TQV", "TO3", "PS", "CLDPRS", "CLDTMP", "H1000", "H250", "H500", "H850", "T2M", "U250", "U500", "V250", "V500"],
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
}

