"""
hard coded paths in cf-forsikring
"""

cf_space             = "/nird/projects/NS9873K/etdu/"
proj                 = "/nird/home/edu061/cf-forsikring/"
data_interim         = proj + "data/interim/"
fig                  = proj + "fig/"

raw                  = cf_space + "raw/"
processed            = cf_space + "processed/"

hindcast_6hourly     = raw + "s2s/mars/ecmwf/hindcast/sfc/6hourly/"
forecast_6hourly     = raw + "s2s/mars/ecmwf/forecast/sfc/6hourly/"

hindcast_daily       = processed + "cf-forsikring/ecmwf/hindcast/daily/"
forecast_daily       = processed + "cf-forsikring/ecmwf/forecast/daily/"

era5_daily_raw       = raw + "era5/daily/"
era5_daily           = processed + "cf-forsikring/era5/daily/"
era5_6hourly         = raw + "era5/6hourly/"

dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "processed":processed,
        "hindcast_6hourly":hindcast_6hourly,
        "forecast_6hourly":forecast_6hourly,
        "hindcast_daily":hindcast_daily,
        "forecast_daily":forecast_daily,        
        "era5_daily_raw":era5_daily_raw,
        "era5_6hourly":era5_6hourly,
        "era5_daily":era5_daily
}        
