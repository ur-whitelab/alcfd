"""
alcfd
Active learning symbolic regression CFD + AI = Wow
"""
import sys
from setuptools import setup, find_packages

short_description = "Active learning symbolic regression CFD + AI = Wow".split("\n")[0]

# from https://github.com/pytest-dev/pytest-runner#conditional-requirement
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

try:
    with open("README.md", "r") as handle:
        long_description = handle.read()
except:
    long_description = None

exec(open('alcfd/version.py').read())

setup(
    # Self-descriptive entries which should always be present
    name='alcfd',
    author='Mehrad Ansari, Heta A. Gandhi, David G. Foster, Andrew D. White', 
    author_email='mehrad.ansari@rochester.edu, heta.gandhi@rochester.edu, andrew.white@rochester.edu',
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ur-whitelab/alcfd',
    version=__version__,
    license='MIT',
    packages=find_packages(),

    # Optional include package data to ship with your package
    # Customize MANIFEST.in if the general case does not suit your needs
    # Comment out this line to prevent the files from being packaged with your software
    # include_package_data=True,

    # Allows `setup.py test` to work correctly with pytest
    setup_requires=[] + pytest_runner,

    # Additional entries you may want simply uncomment the lines you want and fill in the data
     # Required packages, pulls from pip if needed; do not use for Conda deployment
    install_requires=[
        'pandas',
        'modAL'
    ],             
    # platforms=['Linux',
    #            'Mac OS-X',
    #            'Unix',
    #            'Windows'],            # Valid platforms your code works on, adjust to your flavor
    # python_requires=">=3.5",          # Python version restrictions

    # Manual control if final package is compressible or not, set False to prevent the .egg from being made
    # zip_safe=False,

)
