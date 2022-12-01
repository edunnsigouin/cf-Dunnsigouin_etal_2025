"""
hard coded paths in cf-forsikring
"""

cf_space            = "/nird/projects/NS9873K/etdu/"
proj                = "/nird/home/edu061/cf-forsikring/"
data_interim        = proj + "data/interim/"
fig                 = proj + "fig/"
processed           = cf_space + "processed/"
raw                 = cf_space + "raw/"
hindcast_6hourly    = raw + "s2s/mars/ecmwf/hindcast/sfc/6hourly/"
forecast_6hourly    = raw + "s2s/mars/ecmwf/forecast/sfc/6hourly/"
hindcast_daily      = raw + "s2s/mars/ecmwf/hindcast/sfc/daily/"
forecast_daily      = raw + "s2s/mars/ecmwf/forecast/sfc/daily/"

processed_hindcast  = processed + "s2s/mars/ecmwf/hindcast/sfc/"
processed_forecast  = processed + "s2s/mars/ecmwf/forecast/sfc/"
era5_daily          = raw + "era5/daily/"
era5_6hourly        = raw + "era5/6hourly/"

dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "processed":processed,
        "hindcast_6hourly":hindcast_6hourly,
        "forecast_6hourly":forecast_6hourly,
        "hindcast_daily":hindcast_daily,
        "forecast_daily":forecast_daily,        
        "processed_hindcast":processed_hindcast,
        "processed_forecast":processed_forecast,
        "era5_daily":era5_daily,
        "era5_6hourly":era5_6hourly
}        
