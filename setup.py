from setuptools import setup, find_packages

setup(
    name = "MERRA",
    version = "0.1",
    keywords = ("MERRA2", "Solar Energy"),
    description = "Download tool for MERRA2 dataset",
    long_description = "This is a automated tool for MERRA2 data collection and filtering.",
    license = "MIT Licence",

    url = "http://test.com",
    author = "test",
    author_email = "test@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [],

    scripts = [],
    entry_points = {
        'download': [
            'download = downloader.run:download'
        ]
    }
)
