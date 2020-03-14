import requests
import os
import urllib.response
from http import cookiejar
import urllib.error
import urllib.request
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class DownloadManager(object):
    __AUTHENTICATION_URL = 'https://urs.earthdata.nasa.gov/oauth/authorize'
    __username = ''
    __password = ''
    __download_url = ''
    __download_path = ''
    _authenticated_session = None

    def __init__(self, username='', password='', link=None, download_path='download'):
        self.set_username_and_password(username, password)
        self.download_url = link
        self.download_path = download_path

    @property
    def download_url(self):
        return self.__download_url

    @download_url.setter
    def download_url(self, link):
        """
        Setter for the links to download. The links have to be an array containing the URLs. The module will
        figure out the filename from the url and save it to the folder provided with download_path()
        :param links: The links to download
        :type links: List[str]
        """
        # TODO: Check if links have the right structure? Read filename from links?
        # Check if all links are formed properly
        if link is None:
            self.__download_url = ''
        else:
            try:
                self.get_filename(link)
            except AttributeError:
                raise ValueError('The URL seems to not have the right structure: ', item)
            self.__download_url = link

    @property
    def download_path(self):
        return self.__download_path

    @download_path.setter
    def download_path(self, file_path):
        self.__download_path = file_path

    def set_username_and_password(self, username, password):
        self.__username = username
        self.__password = password

    def _mp_download_wrapper(self, url_item):
        """
        Wrapper for parallel download. The function name cannot start with __ due to visibility issues.
        :param url_item:
        :type url_item:
        :return:
        :rtype:
        """
        query = url_item
        file_path = os.path.join(self.download_path, self.get_filename(query))
        self.__download_and_save_file(query, file_path)

    def start_download(self):
        if self._authenticated_session is None:
            self._authenticated_session = self.__create_authenticated_sesseion()
        # Create the download folder.
        os.makedirs(self.download_path, exist_ok=True)
        self._mp_download_wrapper(self.download_url)

    @staticmethod
    def get_filename(url):
        """
        Extracts the filename from the url. This method can also be used to check
        if the links have the correct structure
        :param url: The MERRA URL
        :type url: str
        :return: The filename
        :rtype: str
        """
        # Extract everything between a leading / and .nc4? . The problem with using this without any
        # other classification is, that the URLs have multiple / in their structure. The expressions [^/]* matches
        # everything but /. Combined with the outer expressions, this only matches the part between the last / and .nc4?
        reg_exp = '(\w+)(\.\w+)+(?!.*(\w+)(\.\w+)+)'
        file_name = re.search(reg_exp, url).group(0)
        return file_name

    def __download_and_save_file(self, url, file_path):
        r = self._authenticated_session.get(url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return r.status_code

    def __create_authenticated_sesseion(self):
        s = requests.Session()
        s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'}
        s.auth = (self.__username, self.__password)
        s.cookies = self.__authorize_cookies_with_urllib()
        return s

    def __authorize_cookies_with_urllib(self):
        username = self.__username
        password = self.__password
        top_level_url = "https://urs.earthdata.nasa.gov"

        # create an authorization handler
        p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, top_level_url, username, password);

        auth_handler = urllib.request.HTTPBasicAuthHandler(p)
        auth_cookie_jar = cookiejar.CookieJar()
        cookie_jar = urllib.request.HTTPCookieProcessor(auth_cookie_jar)
        opener = urllib.request.build_opener(auth_handler, cookie_jar)

        urllib.request.install_opener(opener)

        # The merra portal moved the authentication to the download level. Before this change you had to
        # provide username and password on the overview page. For example:
        # goldsmr4.sci.gsfc.nasa.gov/opendap/MERRA2/M2T1NXSLV.5.12.4/
        # authentication_url = 'https://goldsmr4.sci.gsfc.nasa.gov/opendap/MERRA2/M2T1NXSLV.5.12.4/1980/01/MERRA2_100.tavg1_2d_slv_Nx.19800101.nc4.ascii?U2M[0:1:1][0:1:1][0:1:1]'
        # Changes:
        # Authenticate with the first url in the links.
        # Request the website and initialiaze the BasicAuth. This will populate the auth_cookie_jar
        authentication_url = self.download_url
        result = opener.open(authentication_url)

        return auth_cookie_jar

