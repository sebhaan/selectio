# Selectio: Multi-Model Feature Importance Scoring and Auto Feature Selection.

<!-- Badges  start -->

[![PyPI-Server](https://img.shields.io/pypi/v/selectio.svg)](https://pypi.org/project/selectio/)
[![Conda
Version](https://img.shields.io/conda/vn/conda-forge/selectio.svg)](https://anaconda.org/conda-forge/selectio)
[![DOI](https://zenodo.org/badge/541830657.svg)](https://zenodo.org/badge/latestdoi/541830657)
[![License](https://img.shields.io/badge/License-LGPL3-blue)](#license)

<!-- Badges end -->

This Python package computes multiple feature importance scores for  tabulated data and automatically suggests a feature selection based on the majority vote of all models.

<figure>
    <img src="figures/feature_importance.png" alt="Feature Importance">
    <figcaption>Example for multi-model feature importance scores.<figcaption>
</figure> 

## Models

Currently the following models for feature importance scoring are included:
- Spearman rank analysis (see [selectio.models.spearman](selectio/models/spearman.py))
- Correlation coefficient significance of linear/log-scaled Bayesian Linear Regression (see [selectio.models.blr](selectio/models/blr.py))
- Random Forest Permutation test (see [selectio.models.rf](selectio/models/rf.py))
- Random Decision Trees on various subsamples of data (see [selectio.models.rdt](selectio/models/rdt.py))
- Mutual Information Regression (see [selectio.models.mi](selectio/models/mi.py))
- General correlation coefficients (see [selectio.models.xicor](selectio/models/xicor.py))

## Feature Importance Scores and Cross-Correlations

The current feature importance models support numerical data only. Categorical data will need to be encoded to numerical features beforehand.

All model scores are normalized to unity, i.e., $\sum _i^{N_{features}} score_i = 1$

This package includes multiple functions for visualisation of the importance scores and automatic feature ranking. 
	
Feature-to-feature correlations are automatically clustered using hierarchical clustering of the Spearman correlation coefficients (for more details see `utils.plot_feature_correlation_spearman`).


## Installation

To install this package run one of the following:

```bash
conda install -c conda-forge selectio
```

or via pip:

```bash
pip install selectio
```

For development, fork the repository and install dependencies as given in the `environment.yaml` file:
    ```bash
    conda env create -f environment.yaml
    ```


## Usage

There are multiple options to compute feature selection scores: 

### **Option A)** 

as standalone script with a settings file:
```bash
cd selectio
python selectio.py -s <FILENAME>.yaml
```

This will automatically save all scores and selections in csv file and create multiple score plots.

User settings such as input filename and all other options are set in the settings file, which is given in the command line argument with: 
'-s', or '--settings' followed by PATH-TO-FILE/FILENAME.yaml 
(e.g. python selectio.py -s settings/settings_featureimportance.yaml)
If settings-file name is not given, the default settings filename  `settings_featureimportance.yaml` is used. See for settings file template [settings_featureimportance.yaml](selectio/settings/settings_featureimportance.yaml). See for more details [Settings YAML file](#settings-yaml-file).

### **Option B)** 
as function call in python script:
```python
from selectio import selectio
# Read in data from file, generate feature importance plots and save results as csv:
selectio.main('settings_featureimportance.yaml')
```
This will automatically save all scores and selections in csv file and create multiple score plots.

### **Option C)** 
computed directly using the class selectio.Fsel, e.g.

```python
from selectio.selectio import Fsel
# Read in data X (nsample, nfeatures) and y (nsample)
fsel = Fsel(X, y)
# Score features and return results as dataframe:
dfres = fsel.score_models()
```
This returns a table with all scores and feature selections. See for more details and visualisation of scores "Option 2)" in the example notebook `feature_selection.ipynb`.


## Settings YAML file

For settings file template, see [here](https://github.com/sebhaan/selectio/blob/main/selectio/settings/settings_featureimportance.yaml)

The main settings are:
```yaml
# Input data path:
inpath: ...
# File name with numerical data and corresponding covariates:
infname: ...
# Output results path:
outpath: ...
# Name of target for prediction (column name in dataframe):
name_target: ...
# Name or List of features (column names in infname):
# (covariates to be considered )
name_features: 
- ...
- ...
```


## Simulation and Testing

The selectio package provides the option to generate simulated data (see `selectio.simdata`) 
and includes multiple test functions (see `selectio.tests`), e.g.

```python
from selectio import tests
tests.test_select()
```

For more examples and how to create simulated via `simdata.py`, see the provided Jupyter notebooks `feature_selection.ipynb`.


## Adding Custom Model Extensions

More models for feature scoring can be added in the folder 'models' following the existing scripts as example, 
which includes at least:
- a function with name 'factor_importance' that takes X and y as argument and one optional argument norm
- a `__name__` and `__fullname__` attribute
- adding the new module name to the `__init_file__.py` file in the folder models

Other models for feature selections have been considered, such as PCA or SVD-based methods or univariate screening methods (t-test, correlation, etc.). However, some of these models consider either 
only linear relationships, or do not take into account the potential multivariate nature of the data structure  (e.g., higher order interaction between variables). Note that not all included models are completely generalizable, such as Bayesian regression and Spearman ranking given their dependence on monotonic functional behavior.

Since most models have some limitations or rely on certain data assumptions, it is important to consider a variety of techniques for feature selection and to apply model cross-validations.

## Contributions

Contributions are welcome to improve and enhance the Selectio open-source package. To contribute, please start by familiarizing yourself with the project and code structure. For bug reports and feature requests, create a new issue on our GitHub repository. If you're interested in contributing code, documentation, or tests, please fork the repository, create a new branch, and submit a pull request. Be sure to follow the established coding style and guidelines, provide clear and concise commit messages, and thoroughly test your changes. Together, we can make Selectio an even more helpful and reliable tool for everyone.

## License

Copyright (c) 2023 Sebastian Haan

This is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License (LGPL version 3) as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU Lesser General Public License](LICENSE) for more details.

