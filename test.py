import fnmatch
import glob
import os
import shutil
import sys
import tempfile
import download


def test_daily_download_convert():
    var_names = ['rad', 'slv', 'aer']
    delete_temp_dir = False
    download_dir = os.path.join(os.getcwd(), "MERRA2_data")
    download_method = "xr"

    download.daily_download_and_convert(
        var_names, merra2_var_dicts=None, initial_year=2015,
        final_year=2015, initial_month=1, final_month=1, initial_day=1,
        final_day=1, output_dir=download_dir, download_method = download_method,
        delete_temp_dir=delete_temp_dir,
        lat_1=-11, lon_1=-22, lat_2=22, lon_2=33)


if __name__ == "__main__":
    test_daily_download_convert()
