Balancing accuracy versus precision: Enhancing the usability of sub-seasonal forecasts
============

Authors
--------
Etienne Dunn-Sigouin<sup>1</sup>, Erik W. Kolstad<sup>1</sup>,C. Ole Wulff<sup>2</sup>, Douglas J. Parker<sup>2</sup>, and Richard J. Keane<sup>2</sup>.

1: NORCE Norwegian Research Center AS, Bergen, Norway.
2: Bjerknes Centre for Climate Research, Bergen, Norway.
3: School of Earth and Environment, University of Leeds, Leeds, UK.
4: NCAS National Centre for Atmospheric Science, University of Leeds, Leeds, UK.
5: Met Office, Exeter, UK.

Key Points
----------

  - Forecasts often have finer resolution than the scales they can accurately predict
  - Developed user-method to evaluate trade-off between forecast accuracy and precision 
  - Reducing forecast precision improves accuracy and extends predictable lead-times
  - Post-processing forecasts to accurate scales yields more actionable information
  
Abstract
--------
Forecasts are essential for climate adaptation and preparedness, such as in early warning systems and impact
models. A key limitation to their practical use is often their coarse spatial grid spacing. However, another less
frequently discussed but crucial limitation is that forecasts are often more precise than they are accurate when
their grid spacing is finer than the scales they can accurately predict. Here, we adapt the fractions skill score,
a metric conventionally used to quantify spatial forecast accuracy by the meteorological community, to help
users navigate the trade-off between forecast accuracy versus precision. We demonstrate how this trade-off
can be visualized for daily European precipitation, focusing on deterministic predictions of anomalies and
probabilistic predictions of extremes, derived from three years of sub-seasonal forecasts from the European
Centre for Medium-Range Weather Forecasts (ECMWF). Our results show that decreasing precision through
spatial aggregation increases forecast accuracy, extends predictable lead times, and enhances the maximum
possible accuracy relative to the grid scale, while increased precision diminishes these benefits. Notably, spatial
aggregation benefits daily-accumulated forecasts more than weekly-accumulated ones, per unit lead-time. We
demonstrate the practical value of our approach in three examples: communicating early warnings, managing
hydropower capacity, and commercial aviation planning—each characterized by distinct user constraints on
accuracy, spatial scale, or lead-time. The results suggest a different approach for using forecasts; post-processing
forecasts to focus on the most accurate scales rather than the default grid scale, thus offering users more
actionable information.

Status
----------
The paper was published in [Geophysical Research Letters](https://agupubs.onlinelibrary.wiley.com/journal/19448007), [doi: 10.1029/2020GL091540](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2020GL091540). Comments, questions, and suggestions are appreciated. Feedback can be submitted through github [issues](https://github.com/edunnsigouin/cf-Dunnsigouin_etal_2025/issues) or via e-mail to Etienne Dunn-Sigouin (etdu@norceresearch.no).

Data 
----
The model simulations and analysis for this paper were performed using the Norwegian academic high-performance computing and storage facilities maintained by [Sigma2](https://www.sigma2.no/metacenter). The simulations were performed on the [FRAM](https://documentation.sigma2.no/hpc_machines/fram.html) machine and stored and processed on [NIRD](https://documentation.sigma2.no/files_storage/nird.html).

The simulations are run with the [NCAR CESM2.1.0 CAM5 model](https://www.cesm.ucar.edu/models/) in a slab ocean aquaplanet configuration following the [TRACMIP protocol](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2016MS000748). ERA-Interim reanalysis data are available for download from [ECMWF](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era-interim). 

Due to the large volume of raw simulation data (15T), only 'interim' data used to reproduce the figures are included here. Raw and processed data can be made available upon request.

Code setup
-------------
The organization of this project follows loosely from the [cookiecutter-science-project](https://github.com/jbusecke/cookiecutter-science-project) template written by [Julius Busecke](http://jbusecke.github.io/). The project is organized as an installable conda package.

To get setup, first pull the directory from github to your local machine:

``` bash
$ git clone https://github.com/edunnsigouin/cf-Dunnsigouin_etal_2025/
```

Then install the conda environment:

``` bash
$ conda env create -f environment.yml
```

Then install the project package:

``` bash
$ python setup.py develop
```

Finally change the project directory in cf-Dunnsigouin_etal_2025/config.py to your local project directory