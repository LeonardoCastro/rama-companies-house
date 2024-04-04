# Rama, a package to clean, process and analyse Companies House data

This package helps clean, process and analyse the data from the [Companies House API](https://developer.company-information.service.gov.uk/). The package uses a simple cleaning process to create a network of ownership/control between Persons with Significant Control (PSCs) and companies. The aim of the analysis is to understand the legal and fiscal reasons that give rise to the structure of the observed networks.

This package is part of the [Effects of the legal and fiscal framework in UK ownership networks](https://turingcss.org/projects/firms_design/) project of the [Computational Social Science group](https://turingcss.org/) of the [Alan Turing Institute](https://www.turing.ac.uk/).

co-authors of the project: [Dr. Leonardo Castro-Gonzalez](https://www.turing.ac.uk/people/researchers/leonardo-castro-gonzalez), [Dr. Alejandro Beltran](https://www.turing.ac.uk/people/researchers/alejandro-beltran), [Dr. Omar Guerrero](https://www.turing.ac.uk/people/researchers/omar-guerrero).

## Index
- 1. [Installation](#installation)
- 2. [User guide](#user-guide)
- 3. [Contact](#contact)

## Installation

The package is written in Python (minimal version: 3.10). We recommend that the installation is made inside a virtual environment trough `conda`.

### Using conda

The tool `conda`, which comes bundled with Anaconda has the advantage that it lets us specify the version of Python that we want to use. Python>=3.10 is required.

A new environment can be created with

```bash
$ conda create -n rama python=3.10 -y
```

Like before, the environment's name can be anything else instead of `rama` (simply change the name below). We activate it using

```bash
$ conda activate rama
```

### Local installation

Once we are working inside an active virtual environment, we install (the dependencies and) the package by running

```bash
[$ pip install -r requirements.txt]
$ pip install -e .
```

## User guide

Coming soon.

## Contact

- Leonardo Castro-Gonzalez: leonardo_castro@ciencias.unam.mx
- Alejandro Beltran: abeltran@turing.ac.uk
- Omar Guerrero: oguerrero@turing.ac.uk
