import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mediary",
    version="0.1",
    author="Ross Patterson",
    author_email="me@rpatterson.net",
    description=(
        "Media processing and management utilities, "
        "keeping to the Unix DOTADIW philosophy"),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/rpatterson/mediary",
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "Topic :: Multimedia",
        "Topic :: Utilities",
    ],
    install_requires=[
        'service-logging',
    ],
    test_suite="mediary.tests",
    entry_points={
        'console_scripts': [
            'mediary=mediary.command:main'],
    },
)
