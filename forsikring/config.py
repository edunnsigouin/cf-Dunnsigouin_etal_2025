"""
hard coded paths in cf-forsikring
"""

cf_space             = "/nird/projects/NS9873K/etdu/"
proj                 = "/nird/home/edu061/cf-forsikring/"
data_interim         = proj + "data/interim/"
fig                  = proj + "fig/"

raw                  = cf_space + "raw/"
processed            = cf_space + "processed/"
verify               = cf_space + "verify/"

forecast_6hourly      = raw + "s2s/mars/ecmwf/forecast/sfc/6hourly/"
forecast_daily        = processed + "cf-forsikring/ecmwf/forecast/daily/values/"
forecast_daily_binary = processed + "cf-forsikring/ecmwf/forecast/daily/binary/"

hindcast_6hourly      = raw + "s2s/mars/ecmwf/hindcast/sfc/6hourly/"
hindcast_daily        = processed + "cf-forsikring/ecmwf/hindcast/daily/"
hindcast_percentile   = processed + "cf-forsikring/ecmwf/hindcast/percentile/"

era5_6hourly               = raw + "era5/6hourly/"
era5_cont_daily            = processed + "cf-forsikring/era5/continuous-format/daily/"
era5_cont_percentile       = processed + "cf-forsikring/era5/continuous-format/percentile/"
era5_forecast_daily        = processed + "cf-forsikring/era5/model-format/forecast/daily/values/"
era5_forecast_daily_binary = processed + "cf-forsikring/era5/model-format/forecast/daily/binary/"
era5_forecast_clim         = processed + "cf-forsikring/era5/model-format/forecast/climatology/values/"
era5_forecast_clim_binary  = processed + "cf-forsikring/era5/model-format/forecast/climatology/binary/"
era5_forecast_pers         = processed + "cf-forsikring/era5/model-format/forecast/persistence/values/"
era5_forecast_pers_binary  = processed + "cf-forsikring/era5/model-format/forecast/persistence/binary/"
era5_hindcast_percentile   = processed + "cf-forsikring/era5/model-format/hindcast/percentile/"
era5_hindcast_daily        = processed + "cf-forsikring/era5/model-format/hindcast/daily/"

verify_forecast_daily = verify + "cf-forsikring/ecmwf/forecast/daily/"


dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "processed":processed,
        "forecast_6hourly":forecast_6hourly,
        "forecast_daily":forecast_daily,
        "forecast_daily_binary":forecast_daily_binary,
        "hindcast_6hourly":hindcast_6hourly,
        "hindcast_daily":hindcast_daily,
        "hindcast_percentile":hindcast_percentile,
        "era5_6hourly":era5_6hourly,
        "era5_cont_daily":era5_cont_daily,
        "era5_cont_percentile":era5_cont_percentile,
        "era5_forecast_daily":era5_forecast_daily,
        "era5_forecast_daily_binary":era5_forecast_daily_binary,
        "era5_forecast_clim":era5_forecast_clim,
        "era5_forecast_clim_binary":era5_forecast_clim_binary,
        "era5_forecast_pers":era5_forecast_pers,
        "era5_forecast_pers_binary":era5_forecast_pers_binary,
        "era5_hindcast_percentile":era5_hindcast_percentile,
        "era5_hindcast_daily":era5_hindcast_daily,
        "verify_forecast_daily":verify_forecast_daily
}        
