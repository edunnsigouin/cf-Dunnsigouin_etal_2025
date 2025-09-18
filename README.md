Balancing Accuracy Versus Precision: Enhancing the Usability of Sub-Seasonal Forecasts
============

Authors
--------
Etienne Dunn-Sigouin<sup>1,2</sup>, Erik W. Kolstad<sup>1,2</sup>, C. Ole Wulff<sup>1,2</sup>, Douglas J. Parker<sup>1,2,3,4</sup>, and Richard J. Keane<sup>3,5</sup>.

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
The paper was published [here](https://doi.org/10.1016/j.cliser.2025.100594) in the journal Climate Services. Comments, questions, and suggestions are appreciated. Feedback can be submitted through github [issues](https://github.com/edunnsigouin/cf-Dunnsigouin_etal_2025/issues) or via e-mail to Etienne Dunn-Sigouin (etdu@norceresearch.no).


Data 
----
We use three years (2020–2022) of sub-seasonal forecasts and their corresponding hindcasts from the ECMWF downloaded from the [MARS archive](https://www.ecmwf.int/en/forecasts/access-forecasts/access-archive-datasets). We verify the forecasts using ERA5 reanlysis downloaded from the [Copernicus Climate Date Store](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview). 


Setting up the code
-------------

The project is organized as an installable conda package. To get setup, first pull the directory from github to your local machine:

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


Reproducing the paper figures
-------------

The code is split into three steps: 1) downloading, 2) preprocessing, 3) processing, verifying and plotting. In all the script preambles, variable = tp24 should have first_forecast_date = '20200102' and number_forecast = 313 while variable = t2m24 should have first_forecast_date = '20200102' and number_forecast = 209.

1: Downloading

Download reanalysis data using download-era5-sfc-accumulated-6hourly.py for total precipitation and download-era5-sfc-6hourly.py for surface temperature. These scripts download 6 hourly data, concatenate it to daily and then merge them into yearly files.

Download 6hourly subseasonal forecasts and hindcasts using download-s2s-ecmwf-6hourly-forecast.py and download-s2s-ecmwf-6hourly-hindcast.py.

2: Preprocessing

Convert daily reanalysis data into daily s2s forecast and hindcast formats using calc-daily-s2s-forecast-format.py and calc-daily-s2s-hindcast-format.py.

Convert raw 6hourly precipitation s2s forecasts and hindcasts into 6hourly accumulated files using calc-6hourly-accumulated-variables.py. Then, convert the t2m and tp into daily forecast and hindcast files using calc-daily-from-6hourly.py. Finally, create single continuous low resolution forecasts/hindcasts for lead-times 1 to 46 using create-daily-1to46day-low-res-forecast.py. This is because the high res forecasts are from leadday 1 to 15 and the low res forecasts are from leadtime 16 to 46. The code interpolates the highres forecasts to the lowres grid and then stiches it together with the low res forecast to make one long forecast from leadtime 1 to 46.

3: Processing, verifying and plotting

Figure 1: calculate daily era5 and s2s anomalies for the fmsess using process/era5/calc-anomaly-forecast-format.py and process/s2s/calc-anomaly-forecast.py. Calculate daily era5 binaries and s2s probabilities for the fbss using process/era5/calc-binary-forecast-format.py and process/s2s/calc-probability-forecast.py. Calculate the fmsess and fbss using verify/calc-score-s2s-forecast.py. Plot figure 1 using plot/plot-fig-01.py.

Figure 2: calculate the daily spatial fields of daily fmsess and fbss using verify/calc-score-xy-s2s-forecast.py. Plot figure 2 using plot/plot-fig-02.py. 

Figure 3: calculate weekly era5 and s2s anomalies for the fmsess using process/era5/calc-anomaly-forecast-format.py and process/s2s/calc-anomaly-forecast.py. Calculate weekly era5 binaries and s2s probabilities for the fbss using process/era5/calc-binary-forecast-format.py and process/s2s/calc-probability-forecast.py. Calculate the fmsess and fbss using verify/calc-score-s2s-forecast.py. Plot figure 3 using plot/plot-fig-03.py.

Figure 4: calculate the	weekly spatial fields of daily fmsess and fbss using verify/calc-score-xy-s2s-forecast.py. Plot figure 4 using plot/plot-fig-04.py.

Figure 5: calculate daily era5 and s2s anomalies for the scandinavian domain fmsess using process/era5/calc-anomaly-forecast-format.py and process/s2s/calc-anomaly-forecast.py. Calculate daily era5 binaries and s2s probabilities for the scandinavian domain fbss using process/era5/calc-binary-forecast-format.py and process/s2s/calc-probability-forecast.py. Calculate the fmsess and fbss using verify/calc-score-s2s-forecast.py. Plot figure 5 using plot/plot-fig-05.py.

Figure 6: calculate the daily smoothed tp and EVI for era5 data during the hans storm using process/era5/calc-EVI-from-era5-forecast-and-hindcast-for-fig-06.py. Do the same for forecasts of storm hans using process/s2s/calc-EFI-fbss-fmsess-for-figure-6.py. Plot figure 6 using plot/plot-fig-06.py

Figure S1: same as fig. 1 except using season = 'ndjfm' keyword in verify/calc-score-s2s-forecast.py. Plot figure S1 using plot/plot-fig-S1.py.

Figure S2: same	as fig.	1 except using season = 'mjjas' keyword in verify/calc-score-s2s-forecast.py. Plot figure S2 using plot/plot-fig-S2.py.

Figure S3: same	as fig.	1 except using variable = t2m24 instead of tp24 in verify/calc-score-s2s-forecast.py. Plot figure S3 using plot/plot-fig-S3.py.

Figure S4: same as fig. 3 except using variable = t2m24 instead of tp24 in verify/calc-score-s2s-forecast.py. Plot figure S4 using plot/plot-fig-S4.py.

Figure S5: same as fig. 6 except using lead day 7 (date = 2023-08-01). Plot figure S5 using plot/plot-fig-S5.py.

