from multiprocessing import freeze_support
import clearskypy
import os
from getpass import getpass

class dummy_downloader():
    def setUp(self):
        # SIMPLE USE CONFIGURATION
        ## The user should define the input parameters in this script for the easiest use case of the package

        # specify your user authentication
        self.username = input("Please Enter Your USERNAME: ")
        self.password = getpass("Please Enter Your PASSWORD: ")

        # specify the date range
        self.initial_year = 2018
        self.initial_month = 1
        self.initial_day = 1

        # specify the end date
        self.final_year = 2018
        self.final_month = 1
        self.final_day = 3

        # specify the bottom left corner of the rectangular region
        self.lat_1 = -90
        self.lon_1 = -180

        # specify the top left corner of the rectangular region
        self.lat_2 = 90
        self.lon_2 = 180

        # specify the number of threads, this is the number of instances that will run at the same time
        # theoretically, this can be as many as you think your machine can handle, though GESDISC may
        # impose a limit
        self.thread_num = 5

        # specify the output destination of the data, depending on operating system changes the file separator
        # default location is where you run the script, specify here if you want to change it using os.join.
        self.output_dir = os.path.join(os.getcwd(),"MERRA2_data")

        # specify the merge timelapse of the data
        # select from 'none', 'daily', 'monthly', 'yearly'
        self.merge_timelapse = 'monthly'

        # Here you can change what actually gets downloaded
        # full list of variables can be founnd here https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf
        self.merra2_var_dicts = {
                "rad": {
                    "esdt_dir": "M2T1NXRAD.5.12.4",
                    "collection": "tavg1_2d_rad_Nx",
                    "var_name": ["ALBEDO", "CLDTOT", "SWGDN", "SWGDNCLR", "TAUTOT"],
                    "standard_name": "radiation",
                    "least_significant_digit": 3,

                    },
                "slv": {
                    "esdt_dir": "M2T1NXSLV.5.12.4",
                    "collection": "tavg1_2d_slv_Nx",
                    "var_name": ["TQV", "TO3", "PS"],
                    "standard_name": "surface",
                    "least_significant_digit": 3,

                    },
                "aer": {
                    "esdt_dir": "M2T1NXAER.5.12.4",
                    "collection": "tavg1_2d_aer_Nx",
                    "var_name": ["TOTSCATAU", "TOTEXTTAU", "TOTANGSTR"],
                    "standard_name": "aerosols",
                    "least_significant_digit": 3,

                    },
        }

    def download(self):
        clearskypy.downloader.run(
            auth={"uid": self.username, "password": self.password},
            initial_year=self.initial_year,
            final_year=self.final_year,
            initial_month=self.initial_month,
            final_month=self.final_month,
            initial_day=self.initial_day,
            final_day=self.final_day,
            lat_1=self.lat_1,
            lat_2=self.lat_2,
            lon_1=self.lon_1,
            lon_2=self.lon_2,
            thread_num=self.thread_num,
            merra2_var_dicts=self.merra2_var_dicts,
            output_dir=self.output_dir,
            merge_timelapse=self.merge_timelapse
        )


# RUN THE DOWNLOADER
if __name__ == "__main__":
    freeze_support()
    d = dummy_downloader()
    d.setUp()
    d.download()



