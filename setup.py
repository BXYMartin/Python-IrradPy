from setuptools import setup, find_packages
from setuptools.command.test import test
import os
import sys
import unittest
def discover_and_run_tests():
    # get setup.py directory
    setup_file = sys.modules['__main__'].__file__
    setup_dir = os.path.abspath(os.path.dirname(setup_file))

    # use the default shared TestLoader instance
    test_loader = unittest.defaultTestLoader

    # use the basic test runner that outputs to sys.stderr
    test_runner = unittest.TextTestRunner()
    print(os.path.join(setup_dir, "test"))

    # automatically discover all tests
    test_suite = test_loader.discover(os.path.join(setup_dir, "test"), pattern='test_*.py')
    print(test_suite)

    # run the test suite
    test_runner.run(test_suite)

class DiscoverTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        discover_and_run_tests()

setup(
    name = "MERRA2_CSM",
    version = "1.0",
    keywords = ("MERRA2", "Clear Sky Model", "Solar Energy"),
    description = "Download tool for MERRA2 dataset for Clear Sky Model.",
    long_description = "This is a automated tool for MERRA2 data collection and filtering, for the analysis of Clear Sky Model.",
    license = "MIT Licence",

    url = "Not Available",
    author = "Jamie Bright, Yue Zhang, Martin Bai",
    author_email = "Not Available",

    packages = find_packages(exclude=['test']),
    include_package_data = True,
    platforms = "any",
    install_requires = [
        "pydap",
        "xarray",
        "config",
        "scipy",
        "utils",
        "netCDF4",
        "numpy",
        "pathlib",
        "typing",
        "requests",
        "argparse",
        ],

    scripts = [],
    cmdclass = {'test': DiscoverTest},
    entry_points = {
        'console_scripts': [
            'merra2_downloader = MERRA2_CSM.downloader.socket:main'
        ]
    }
)
