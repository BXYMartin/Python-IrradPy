from setuptools import setup, find_packages

setup(
    name = "MERRA2_CSM",
    version = "0.2",
    keywords = ("MERRA2", "Clear Sky Model", "Solar Energy"),
    description = "Download tool for MERRA2 dataset for Clear Sky Model.",
    long_description = "This is a automated tool for MERRA2 data collection and filtering, for the analysis of Clear Sky Model.",
    license = "MIT Licence",

    url = "Not Available",
    author = "Jamie Bright, Yue Zhang, Martin Bai",
    author_email = "Not Available",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [
        "pydap",
        "xarray",
        "config",
        "utils",
        "netCDF4",
        "numpy",
        "pathlib",
        "typing",
        "requests",
        "argparse",
        ],

    scripts = [],
    entry_points = {
        'console_scripts': [
            'merra2_downloader = MERRA2_CSM.downloader.socket:run'
        ]
    }
)
