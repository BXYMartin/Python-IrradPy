import datetime
import shutil
import subprocess
import sys
import os
import tempfile
import netCDF4
import numpy as np
import numpy.ma as ma
from calendar import monthrange
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union
from variables import var_list

defi2 = netCDF4.default_fillvals["i2"]
defi4 = netCDF4.default_fillvals["i4"]
deff4 = netCDF4.default_fillvals["f4"]

KiB = 2 ** 10
MiB = 2 ** 20
GiB = 2 ** 30

def subdaily_download(
    merra2_server: str,
    dataset_esdt: str,
    merra2_collection: str,
    initial_year: int,
    final_year: int,
    initial_month: int = 1,
    final_month: int = 12,
    initial_day: int = 1,
    final_day: Optional[int] = None,
    output_directory: Union[str, Path] = None,
):
    """
    MERRA2 subdaily download.

    Parameters
    ----------
    merra2_server : str
        Must contain trailing slash.
        e.g. https://goldsmr4.gesdisc.eosdis.nasa.gov/data/
    dataset_esdt : str
    merra2_collection : str
    initial_year : int
    final_year : int
    initial_month : int
    final_month : int
    initial_day : int
    final_day : Optional[int]
    output_directory : Union[str, Path]
    """

    if output_directory is None:
        add_output_dir = ""
    else:
        add_output_dir = "--directory-prefix={0}".format(output_directory)

    if not isinstance(output_directory, Path):
        log_file = Path(output_directory)

    log_file = os.path.join(log_file.parent, 'index.npy')
    if os.path.exists(log_file):
        log = np.load(log_file).tolist()
    else:
        log = []

    data_path = "MERRA2/{4}/{0}/{1}/" "MERRA2_{3}.{5}.{0}{1}{2}.nc4"
    for yyyy in range(initial_year, final_year + 1):
        if yyyy < 1992:
            merra_stream = "100"
        elif yyyy < 2001:
            merra_stream = "200"
        elif yyyy < 2011:
            merra_stream = "300"
        else:
            merra_stream = "400"
        if yyyy == initial_year:
            mi = initial_month
        else:
            mi = 1
        if yyyy == final_year:
            mf = final_month
        else:
            mf = 12
        for mm in range(mi, mf + 1):
            if (yyyy == initial_year) and (mm == mi):
                di = initial_day
            else:
                di = 1
            if final_day and (yyyy == final_year) and (mm == mf):
                df = final_day
            else:
                mrange = monthrange(yyyy, mm)
                df = mrange[1]
            for dd in range(di, df + 1):
                cdp = data_path.format(
                    str(yyyy),
                    str(mm).zfill(2),
                    str(dd).zfill(2),
                    merra_stream,
                    dataset_esdt,
                    merra2_collection,
                )

                if cdp in log:
                    print("Skipping existing file " + cdp)
                    continue
                else:
                    log.append(cdp)

                subprocess.call(
                    [
                        "wget",
                        "-c",
                        add_output_dir,
                        "--load-cookies",
                        str(Path("~/.urs_cookies").expanduser()),
                        "--save-cookies",
                        str(Path("~/.urs_cookies").expanduser()),
                        "--keep-session-cookies",
                        merra2_server + cdp,
                    ]
                )
    np.save(log_file, np.array(log))


def daily_netcdf(
    path_data: Union[str, Path],
    output_file: Union[str, Path],
    var_name: str,
    initial_year: int,
    final_year: int,
    merra2_var_dict: Optional[dict] = None,
    verbose: bool = False,
):
    """MERRA2 daily NetCDF.

    Parameters
    ----------
    path_data : Union[str, Path]
    output_file : Union[str, Path]
    var_name : str
    initial_year : int
    final_year : int
    merra2_var_dict : Optional[dict]
        Dictionary containing the following keys:
        esdt_dir, collection, merra_name, standard_name,
        see the Bosilovich paper for details.
    verbose : bool

    """
    if not isinstance(path_data, Path):
        path_data = Path(path_data)

    if not merra2_var_dict:
        merra2_var_dict = var_list[var_name]

    search_str = "*{0}*.nc4".format(merra2_var_dict["collection"])
    nc_files = [str(f) for f in path_data.rglob(search_str)]
    if os.path.exists(output_file) and len(os.listdir(path_data)) != 0:
        shutil.copy(output_file, path_data)
        filepath, filename = os.path.split(output_file)
        nc_files.append(os.path.join(path_data, filename))
    nc_files.sort()

    relevant_files = []
    divided_files = [[]]
    nt_division = [0]
    nt = 0
    nmb = 0
    for nc_file in nc_files:
        try:
            yyyy = int(nc_file.split(".")[-2][0:4])
        except ValueError:
            yyyy = int(nc_file.split(".")[-2][-4:])
        if (yyyy >= initial_year) and (yyyy <= final_year):
            relevant_files.append(nc_file)
            nc = netCDF4.Dataset(nc_file, "r")
            divided_files[-1].append(nc_file)
            nt_division[-1] += len(nc.dimensions["time"])
            nt += len(nc.dimensions["time"])
            nc.close()

    if len(relevant_files) == 0:
        if verbose:
            print(str(merra2_var_dict["merra_name"]) + " data files have been downloaded and merged for " + var_name + ".")
        return
    nc_reference = netCDF4.Dataset(relevant_files[0], "r")

    if isinstance(merra2_var_dict["merra_name"], list):
        var_ref = {}
        for name in merra2_var_dict["merra_name"]:
            var_ref[name] = nc_reference.variables[name]
    else:
        var_ref = nc_reference.variables[merra2_var_dict["merra_name"]]

    nc_file = output_file

    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    nc1 = netCDF4.Dataset(nc_file, "w", format="NETCDF4_CLASSIC")

    nc1.Conventions = "CF-1.7"

    nc1.title = (
        "Modern-Era Retrospective analysis for Research and " "Applications, Version 2"
    )
    if (len(divided_files) == 1) and (len(divided_files[0]) == 1):
        nc1.history = (
            "{0}\n{1}: " "Reformat to CF-1.7 & " "Extract variable."
        ).format(nc_reference.History, now)
    else:
        nc1.history = (
            "{0}\n{1}: "
            "Reformat to CF-1.7 & "
            "Extract variable & "
            "Merge in time."
        ).format(nc_reference.History, now)
    nc1.institution = nc_reference.Institution
    nc1.source = "Reanalysis"
    nc1.references = nc_reference.References

    attr_overwrite = ["conventions", "title", "institution", "source", "references"]
    ordered_attr = {}
    for attr in nc_reference.ncattrs():
        if attr == "History":
            continue
        if attr.lower() in attr_overwrite:
            ordered_attr["original_file_" + attr] = getattr(nc_reference, attr)
        else:
            ordered_attr[attr] = getattr(nc_reference, attr)
    for attr in sorted(ordered_attr.keys(), key=lambda v: v.lower()):
        setattr(nc1, attr, ordered_attr[attr])

    # Create netCDF dimensions
    nc1.createDimension("time", nt)
    # nc1.createDimension('ts', 6)
    # nc1.createDimension('level', k)
    nc1.createDimension("lat", len(nc_reference.dimensions["lat"]))
    nc1.createDimension("lon", len(nc_reference.dimensions["lon"]))
    if merra2_var_dict["cell_methods"]:
        nc1.createDimension("nv", 2)

    time = nc1.createVariable("time", "i4", ("time",), zlib=True)
    time.axis = "T"
    time.units = "hours since 1980-01-01 00:00:00"
    time.long_name = "time"
    time.standard_name = "time"
    time.calendar = "gregorian"

    tbounds = None
    if merra2_var_dict["cell_methods"]:
        time.bounds = "time_bnds"
        tbounds = nc1.createVariable("time_bnds", "i4", ("time", "nv"))

    # level = nc1.createVariable('level','f4',('level',),zlib=True)
    # level.axis = 'Z'
    # level.units = 'Pa'
    # level.positive = 'up'
    # level.long_name = 'air_pressure'
    # level.standard_name = 'air_pressure'

    lat = nc1.createVariable("lat", "f4", ("lat",), zlib=True)
    lat.axis = "Y"
    lat.units = "degrees_north"
    lat.long_name = "latitude"
    lat.standard_name = "latitude"
    lat[:] = nc_reference.variables["lat"][:]

    lon = nc1.createVariable("lon", "f4", ("lon",), zlib=True)
    lon.axis = "X"
    lon.units = "degrees_east"
    lon.long_name = "longitude"
    lon.standard_name = "longitude"
    lon[:] = nc_reference.variables["lon"][:]

    least_digit = merra2_var_dict.get("least_significant_digit", None)

    if isinstance(merra2_var_dict["merra_name"], list):
        var1 = {}
        for name in merra2_var_dict["merra_name"]:
            var1[name] = nc1.createVariable(
                name,
                "f4",
                ("time", "lat", "lon"),
                zlib=True,
                fill_value=deff4,
                least_significant_digit=least_digit,
            )
            var1[name].units = var_ref[name].units
            var1[name].long_name = var_ref[name].long_name
            var1[name].standard_name = merra2_var_dict["standard_name"]
            if merra2_var_dict["cell_methods"]:
                var1[name].cell_methods = merra2_var_dict["cell_methods"]
    else:
        var1 = nc1.createVariable(
            merra2_var_dict["merra_name"],
            "f4",
            ("time", "lat", "lon"),
            zlib=True,
            fill_value=deff4,
            least_significant_digit=least_digit,
        )
        var1.units = var_ref.units
        var1.long_name = var_ref.long_name
        var1.standard_name = merra2_var_dict["standard_name"]
        if merra2_var_dict["cell_methods"]:
            var1.cell_methods = merra2_var_dict["cell_methods"]

    nc_reference.close()

    t = 0
    for i, division in enumerate(divided_files):
        if isinstance(merra2_var_dict["merra_name"], list):
            tmp_data = {}
            for name in merra2_var_dict["merra_name"]:
                tmp_data[name] = ma.masked_all(
                    [nt_division[i], len(nc1.dimensions["lat"]), len(nc1.dimensions["lon"])]
                )
        else:
            tmp_data = ma.masked_all(
                [nt_division[i], len(nc1.dimensions["lat"]), len(nc1.dimensions["lon"])]
            )
        tmp_time = ma.masked_all([nt_division[i]])
        ttmp = 0
        for nc_file in division:
            if verbose:
                print(nc_file)
            nc = netCDF4.Dataset(nc_file, "r")
            if isinstance(merra2_var_dict["merra_name"], list):
                ncvar = {}
                for name in merra2_var_dict["merra_name"]:
                    ncvar[name] = nc.variables[name]
            else:
                ncvar = nc.variables[merra2_var_dict["merra_name"]]
            nctime = nc.variables["time"]
            ncdatetime = netCDF4.num2date(nctime[:], nctime.units)
            nctime_1980 = np.round(netCDF4.date2num(ncdatetime, time.units))
            if isinstance(merra2_var_dict["merra_name"], list):
                for name in merra2_var_dict["merra_name"]:
                    tmp_data[name][ttmp : ttmp + ncvar[name].shape[0], :, :] = ncvar[name][:, :, :]
                    tmp_time[ttmp : ttmp + ncvar[name].shape[0]] = nctime_1980[:]
                    ttmp += ncvar[name].shape[0]
            else:
                tmp_data[ttmp : ttmp + ncvar.shape[0], :, :] = ncvar[:, :, :]
                tmp_time[ttmp : ttmp + ncvar.shape[0]] = nctime_1980[:]
                ttmp += ncvar.shape[0]
            nc.close()
        if isinstance(merra2_var_dict["merra_name"], list):
            for name in merra2_var_dict["merra_name"]:
                var1[name][t : t + tmp_data[name].shape[0], :, :] = tmp_data[name][:, :, :]
                time[t : t + tmp_data[name].shape[0]] = tmp_time[:]
            if merra2_var_dict["cell_methods"]:
                tbounds[t : t + tmp_data[merra2_var_dict["merra_name"][0]].shape[0], 0] = tmp_time[:] - 12
                tbounds[t : t + tmp_data[merra2_var_dict["merra_name"][0]].shape[0], 1] = tmp_time[:] + 12
            t += tmp_data[merra2_var_dict["merra_name"][0]].shape[0]
        else:
            var1[t : t + tmp_data.shape[0], :, :] = tmp_data[:, :, :]
            time[t : t + tmp_data.shape[0]] = tmp_time[:]
            if merra2_var_dict["cell_methods"]:
                tbounds[t : t + tmp_data.shape[0], 0] = tmp_time[:] - 12
                tbounds[t : t + tmp_data.shape[0], 1] = tmp_time[:] + 12
            t += tmp_data.shape[0]

    nc1.close()


def daily_download_and_convert(
    merra2_server: str,
    var_names: List[str],
    initial_year: int,
    final_year: int,
    initial_month: int = 1,
    final_month: int = 12,
    initial_day: int = 1,
    final_day: Optional[int] = None,
    merra2_var_dicts: Optional[List[dict]] = None,
    output_dir: Union[str, Path] = None,
    delete_temp_dir: bool = True,
    verbose: bool = True,
):
    """MERRA2 daily download and conversion.

    Parameters
    ----------
    merra2_server : str
        Must contain trailing slash.
        e.g. https://goldsmr4.gesdisc.eosdis.nasa.gov/data/
    var_names : List[str]
        Variable short names, must be defined in variables.py
        if merra2_var_dict is not provided. If more than one variable,
        they are assumed to have the same original files and those will only
        be downloaded once.
    initial_year : int
    final_year : int
    initial_month : int
    final_month : int
    initial_day : int
    final_day : Optional[int]
    merra2_var_dicts : Optional[List[dict]]
        Dictionary containing the following keys:
        esdt_dir, collection, merra_name, standard_name,
        see the Bosilovich paper for details. Same order as var_names.
    output_dir : Union[str, Path]
    delete_temp_dir : bool
    verbose : bool
    """
    try:
        if isinstance(output_dir, Path):
            output_dir = Path(output_dir)
        if output_dir is None:
            output_dir = Path.cwd()
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if (2, 7) < sys.version_info < (3, 6):
            output_dir = str(output_dir)

        temp_dir_download = tempfile.mkdtemp(dir=output_dir)
        for i, var_name in enumerate(var_names):
            if not merra2_var_dicts:
                merra2_var_dict = var_list[var_name]
            else:
                merra2_var_dict = merra2_var_dicts[i]
            # Download subdaily files
            if i == 0:
                subdaily_download(
                    merra2_server,
                    merra2_var_dict["esdt_dir"],
                    merra2_var_dict["collection"],
                    initial_year,
                    final_year,
                    initial_month=initial_month,
                    final_month=final_month,
                    initial_day=initial_day,
                    final_day=final_day,
                    output_directory=temp_dir_download,
                )
            # Name the output file
            if initial_year == final_year:
                file_name_str = "{0}_day_merra2_reanalysis_{1}.nc4"
                out_file_name = file_name_str.format(var_name, str(initial_year))
            else:
                file_name_str = "{0}_day_merra2_reanalysis_{1}-{2}.nc4"
                out_file_name = file_name_str.format(
                    var_name, str(initial_year), str(final_year)
                )
            out_file = Path(output_dir).joinpath(out_file_name)
            # Extract variable
            daily_netcdf(
                temp_dir_download,
                out_file,
                var_name,
                initial_year,
                final_year,
                verbose=verbose,
            )
        if delete_temp_dir:
            shutil.rmtree(temp_dir_download)
    except BaseException:
        shutil.rmtree(output_dir)
        print("Error occurred in runtime, exiting...")
