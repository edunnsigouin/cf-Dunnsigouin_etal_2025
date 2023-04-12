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

hindcast_6hourly      = raw + "s2s/mars/ecmwf/hindcast/sfc/6hourly/"
forecast_6hourly      = raw + "s2s/mars/ecmwf/forecast/sfc/6hourly/"
hindcast_model_daily  = processed + "cf-forsikring/ecmwf/hindcast/model-format/daily/"
forecast_model_daily  = processed + "cf-forsikring/ecmwf/forecast/model-format/daily/"
forecast_binary_daily = processed + "cf-forsikring/ecmwf/forecast/model-format/binary/daily/"
hindcast_percentile   = processed + "cf-forsikring/ecmwf/hindcast/percentile/"

era5_6hourly         = raw + "era5/6hourly/"
era5_cont_daily      = processed + "cf-forsikring/era5/continuous-format/daily/"
era5_model_clim      = processed + "cf-forsikring/era5/model-format/climatology/"
era5_model_daily     = processed + "cf-forsikring/era5/model-format/daily/"
era5_model_pers      = processed + "cf-forsikring/era5/model-format/persistence/"
era5_percentile      = processed + "cf-forsikring/era5/percentile/"
era5_binary_daily    = processed + "cf-forsikring/era5/model-format/binary/daily/"
era5_binary_clim     = processed + "cf-forsikring/era5/model-format/binary/climatology/"

verify_forecast_daily = verify + "cf-forsikring/ecmwf/forecast/daily/"


dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "processed":processed,
        "hindcast_6hourly":hindcast_6hourly,
        "forecast_6hourly":forecast_6hourly,
        "hindcast_model_daily":hindcast_model_daily,
        "forecast_model_daily":forecast_model_daily,
        "forecast_binary_daily":forecast_binary_daily,
        "hindcast_percentile":hindcast_percentile,
        "era5_6hourly":era5_6hourly,
        "era5_cont_daily":era5_cont_daily,
        "era5_model_clim":era5_model_clim,
        "era5_model_daily":era5_model_daily,
        "era5_model_pers":era5_model_pers,
        "era5_percentile":era5_percentile,
        "era5_binary_daily":era5_binary_daily,
        "era5_binary_clim":era5_binary_clim,
        "verify_forecast_daily":verify_forecast_daily
}        
