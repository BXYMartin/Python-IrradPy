#!/usr/bin/env python
# encoding: utf-8

import os
import re
import datetime
import traceback
import numpy as np
from typing import Optional
from typing import Union
from pathlib import Path
from gzip import GzipFile
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
from .download import FtpDownloader


class SocketManager:
    def run(self,
            download_directory: Optional[Union[str, Path]] = None
            ):
        if download_directory is None:
            download_directory = os.path.join(os.getcwd(), 'BSRN_data')
        self.synchronize(download_directory)
        self.conversion(download_directory)

    def synchronize(self, download_directory):
        try:
            fd = FtpDownloader(
                host = 'ftp.bsrn.awi.de',
                user = 'bsrnftp',
                passwd = 'bsrn1',
                port=21,
                timeout=60
            )
            numDir, numFile, numUnknown, numDownErr = fd.downloadDir(
                rdir='.',
                ldir=download_directory,
                tree=None,
                errHandleFunc=None,
                verbose=True
            )
        except Exception as err:
            traceback.print_exc()

    def check_metadata(self, meta_file, force_update=False):
        meta_data = []
        headers = ['name', 'code', 'location',
                'latitude', 'longitude', 'elevation', 'startdate', 'enddate']
        update = False
        with open(meta_file, 'r') as meta:
            timestamp = False
            for line in meta:
                if not timestamp:
                    timestamp = line
                    create = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
                    update = not force_update and (datetime.date.today().year-create.year)*12 + datetime.date.today().month-create.month==0
                    continue
                if len(line.split(',')) != len(headers):
                    continue
                meta_data.append(dict(zip(headers,line.split(','))))

        if update:
            if force_update:
                print("Forced Update Metadata From Server...")
            else:
                print("Metadata Outdated, Updating From Server...")
            # Updating Metadata
            try:
                fd = FtpDownloader(
                    host = 'ftp.bsrn.awi.de',
                    user = 'bsrnftp',
                    passwd = 'bsrn1',
                    port=21,
                    timeout=60
                )
                meta_data = fd.syncIndex(meta_data)
                with open(meta_file, "w") as meta:
                    meta.write(datetime.date.today().strftime('%Y-%m-%d') + '\n')
                    for site in meta_data:
                        meta.write(",".join(site.values()) + "\n")
            except Exception as err:
                traceback.print_exc()
        else:
            return meta_data

    def conversion(self, data_directory):
        for file in os.listdir(data_directory):
            file_path = os.path.join(data_directory, file)
            if not os.path.isdir(file_path) or file in ["zz_bin"]:
                continue
            print("Processing Site %s..." % file)
            search_str = "*.dat.gz"
            gz_files = [str(f) for f in Path(file_path).rglob(search_str)]
            # GunZip All The Files
            widgets = ['Extracting: ', Percentage(), ' ', Bar(marker='#',left='[',right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
            pbar = ProgressBar(widgets=widgets, maxval=len(gz_files))
            pbar.start()

            for gz_file in gz_files:
                temppath, tempname = os.path.split(gz_file)
                shortname, extension = os.path.splitext(tempname)
                gz_file = GzipFile(gz_file)
                open(os.path.join(file_path, shortname), "wb").write(gz_file.read())
                pbar.update(pbar.currval + 1)
                gz_file.close()

            pbar.update()
            pbar.finish()
            search_str = "???????.dat"
            dat_files = [str(f) for f in Path(file_path).rglob(search_str)]
            dat_filedates = [[int("".join(filter(str.isdigit, os.path.split(path)[1]))[0:2]),
                int("".join(filter(str.isdigit, os.path.split(path)[1]))[2:4])] for path in dat_files]
            # Get Dates
            readable_dates = []
            for date in dat_filedates:
                if date[1] > 50:
                    date[1] += 1900
                else:
                    date[1] += 2000
                readable_dates.append(date[1] * 12 + date[0])
            from_date = min(readable_dates)
            till_date = max(readable_dates) + 1

            data_length = datetime.datetime(int((till_date-1) / 12), int((till_date-1) % 12 + 1), 1) - datetime.datetime(int((from_date-1) / 12), int((from_date-1) % 12 + 1), 1)
            # Headers Definition
            data_headers = ['day_of_month','minute_of_day','G_irrad','G_stddev',
                    'G_min','G_max','B','B_stddev','B_min','B_max','D','D_stddev',
                    'D_min','D_max','dlwr','dlwr_stddev','dlwr_min','dlwr_max',
                    'air_temp_at_dlwr_height','rh_at_dlwr_height','p_at_dlwr_height'];
            site_data = np.full((data_length.days * 60 * 24, len(data_headers)), np.nan, dtype="float")
            site_info = {"contact": [], "location": []}

            for dat_index, dat_file in enumerate(dat_files):
                with open(dat_file, "r") as dat:
                    content = "".join(dat.readlines())
                    site_code = file
                    site_month = dat_filedates[dat_index][0]
                    site_year = dat_filedates[dat_index][1]
                    # Parse Site Info
                    ## Parse Site Contact Info
                    print("Extracting Info For Site %s..." % site_code)
                    result = re.search(r'[CU]0002\n', content)
                    if result is not None:
                        contacts = content[result.end():]
                        result = re.search(r'\n\*[CU]', contacts)
                        if result is not None:
                            contacts = contacts[:result.start()]
                            contacts = contacts.split(" -1 -1 -1")
                            for contact in contacts:
                                contact = contact.split("\n")
                                lines = list(filter(lambda x : x, contact))
                                if len(lines) == 0:
                                    continue
                                for index, item in enumerate(lines):
                                    lines[index] = " ".join(item.split())
                                if lines not in site_info["contact"]:
                                    site_info["contact"].append(lines)
                    ## Parse Site Location Info
                    result = re.search(r'[CU]0004\n', content)
                    if result is not None:
                        locations = content[result.end():]
                        result = re.search(r'\n\*[CU]', locations)
                        if result is not None:
                            locations = locations[:result.start()]
                            locations = locations.split(" -1 -1 -1")
                            for location in locations:
                                location = location.replace("-1 -1", "")
                                location = location.split("\n")
                                lines = list(filter(lambda x : x.strip(), location))
                                if len(lines) == 0:
                                    continue
                                for index, item in enumerate(lines):
                                    lines[index] = " ".join(item.split())
                                if lines not in site_info["location"]:
                                    site_info["location"].append(lines)

                    data_offset = datetime.datetime(site_year, site_month, 1) - datetime.datetime(int((from_date-1) / 12), int((from_date-1) % 12 + 1), 1)
                    data_offset = data_offset.days * 60 * 24
                    result = re.search(r'[CU]0008[ \-0-9\n ]*([YN])', content)
                    if result is not None:
                        rad_measure = result.group(1)
                    else:
                        rad_measure = "N"
                    # Special Treatments
                    if site_code in ["tat", "reg"]:
                        rad_measure = "Y"
                    # Contains Radiation Measurements
                    if rad_measure != "Y":
                        print("Site %s Does not Contain Radiation Measurements" % site_code)
                        continue
                    result = re.search(r'[CU]0100\n', content)
                    if result is None:
                        print("Site %s Failed To Get Data Header" % site_code)
                        continue
                    # Get Data Area
                    content = content[result.end():]
                    result = re.search(r'\n\*', content)
                    if result is not None:
                        content = content[:result.start()]
                    # Remove Extra Data Area
                    data_array = np.array(content.split()).astype("float")
                    if len(data_array) == 0:
                        print("Site %s Failed With No Available Data" % site_code)
                        continue
                    data_array = np.reshape(data_array, (-1, len(data_headers)))
                    # Handle Strange Values
                    data_array[data_array == -999] = np.nan
                    data_array[data_array == -99.9] = np.nan
                    if site_month == 12:
                        days = datetime.datetime(site_year+1, 1, 1) - datetime.datetime(site_year, site_month, 1)
                    else:
                        days = datetime.datetime(site_year, site_month+1, 1) - datetime.datetime(site_year, site_month, 1)
                    # Uniformed Data Length
                    minutes = days.days * 60 * 24;
                    timestamp = datetime.datetime(site_year, site_month, 1).timestamp()
                    if len(data_array) == minutes:
                        widgets = ['Processing %d-%s: ' % (site_year, str(site_month).zfill(2)), Percentage(), ' ', Bar(marker='#',left='[',right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
                        pbar = ProgressBar(widgets=widgets, maxval=minutes)
                        pbar.start()
                        for i in range(0, minutes):
                            site_data[data_offset+i] = data_array[i]
                            site_data[data_offset+i][0:2] = timestamp + i * 60
                            pbar.update(pbar.currval + 1)
                        pbar.update()
                        pbar.finish()
                    else:
                        widgets = ['Processing %d-%s: ' % (site_year, str(site_month).zfill(2)), Percentage(), ' ', Bar(marker='#',left='[',right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
                        pbar = ProgressBar(widgets=widgets, maxval=minutes)
                        pbar.start()
                        for i in range(0, minutes):
                            closest_distance = 30 * 24 * 60
                            closest_item = data_array[0]
                            for item in data_array:
                                item_offset = (item[0] - 1) * 60 * 24 + item[1]
                                if closest_distance > abs(i-item_offset):
                                    closest_distance = abs(i-item_offset)
                                    closest_item = item
                            site_data[i+data_offset] = closest_item
                            site_data[i+data_offset][0:2] = timestamp + i * 60
                            pbar.update(pbar.currval + 1)
                        pbar.update()
                        pbar.finish()
            print("Saving Files For Site %s..." % file)
            save_path = os.path.join(file_path, '%s.npy' % file)
            np.save(save_path, site_data)

            print(site_info)
            info_path = os.path.join(file_path, '%s.txt' % file)
            with open(info_path, "w") as info:
                info.write(str(site_info))
            new_data_headers = ['unix_timestamp','G_irrad','G_stddev',
                    'G_min','G_max','B','B_stddev','B_min','B_max','D','D_stddev',
                    'D_min','D_max','dlwr','dlwr_stddev','dlwr_min','dlwr_max',
                    'air_temp_at_dlwr_height','rh_at_dlwr_height','p_at_dlwr_height'];

            print("Deleting Unzipped Files For Site %s..." % file)
            for delete_file in dat_files:
                os.remove(delete_file)
            print("Finished Conversion For Site %s" % file)
