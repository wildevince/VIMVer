# Viral Instrant Mutation Viewer


## About ##

Instant Variant is a web-service bioinformatics software.
The goal of this project is to propose a bioinformatics tool for structural protein studies. 
Under [CeCCIL](http://www.cecill.info/index.en.html) license.

## Requirements

We have implemented this project in **python 3.8+**, along with three python packages :

* [Python Django framework](https://www.djangoproject.com/)
* [Biopython](https://www.djangoproject.com/)
* [logomaker](https://logomaker.readthedocs.io/en/latest/)
* [numpy](https://numpy.org/)

## Installation

1. The code is available via the following github repository: https://github.com/wildevince/ViralOceanView.git.
```
git clone https://github.com/wildevince/ViralOceanView.git
```

2. We recommande to install the project with a python virtual environment.

3. If needed to verify your python version and install the required packages.

#### Verify your python version ####
```
python3 --version
```

#### install the required packages ####
```
python3 -m pip install -r requirements.txt
```

#### Verify your django version ####
```
python3 -m  django --version
```

## Usage

The project is deployed with apache2 service (via this link https://vimver.afmb.univ-mrs.fr/).

1. Paste your SARS-CoV2 related genomic sequence in the input box. Then press the 'Blast it' button underneath.

<img src="/ViralOceanView/static/OceanViewer/img/help_1.png" style="width: 80%">

2. Press the newly appeared button to jump to the result.

<img src="/ViralOceanView/static/OceanViewer/img/help_2.png" style="width: 80%">

3. Press the 'pick' button to acces the alignements for the corresponding line in the table.


### Deployment
We used a apache2 server for the deployment. Please check Django documentation.


## Citation
work in progress


## Contacts
vincent.wilde@univ-amu.fr
