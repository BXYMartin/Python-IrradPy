import irradpy
import os

if __name__ == '__main__':
    # download directory is ./BSRN_data
    # download could be time-consuming since BSRN is using FTP Sync
    download_directory = os.path.join(os.getcwd(), 'BSRN_data')
    irradpy.downloader.bsrn.run(download_directory)
    # downloader will extract all the data from the text files into site_name.npy under each site directory
    # you can use the numpy file directly or use the extractor
    # extract data for BSRN
    extracted_data = irradpy.extractor.extract_for_BSRN(download_directory)
    # print extracted data
    print(extracted_data)
