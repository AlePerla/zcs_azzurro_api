from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="zcs_azzurro_api",
    version="2023.02.1",
    author="Alessandro Perla",
    author_email="sys.ale.perla@gmail.com",
    description="Unofficial ZCS Azzurro client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlePerla/zcs_azzurro_api",
    install_requires=[
        'requests',
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)
