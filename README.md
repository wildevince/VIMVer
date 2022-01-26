# Instant Variant

This Readme file is intended for developpers or for any other users.
**Requirements**, **Installation** and **Usage** are described below.

## About ##

Instant Variant is a web-service bioinformatics software.
The goal of this project is to propose a bioinformatics tool for structural protein studies.


## Requirements

We have implemented this project in **python 3.6+**, along with three python packages :

* [Python Django framework](https://www.djangoproject.com/)
* [Biopython](https://www.djangoproject.com/)
* [logomaker](https://logomaker.readthedocs.io/en/latest/)


## Installation

The project is still in developper's mode. That means that it will be running in a local server manage by Django.

1. The code is available via the following github repository : https://github.com/wildevince/ViralOceanView.git.
```
git clone https://github.com/wildevince/ViralOceanView.git
```

2. If needed to verify your python version and to install the required packages.

#### Verify your python version ####
```
python3 --version
```

#### install the required packages ####
```
python3 -m pip install django
python3 -m pip install Bio
python3 -m pip install logomaker
```

#### Verify your django version ####
```
python3 -m  django --version
```

## Usage

To run the web-service in the dedicaded local-server by django.
```
python3 ./runInstantVariant.sh
```

###


### Deployment
work in progress


### Specifications
work in progress
Precision on certain functionalities.


### Documentation

The documentation, in `.html` format, is in the `ViralOceanView/docs/` project repository.


## Citation
work in progress


## Contacts
vincent.wilde@univ-amu.fr
