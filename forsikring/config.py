"""
hard coded paths in cf-forsikring
"""

cf_space             = "/nird/projects/NS9873K/etdu/"
proj                 = "/nird/home/edu061/cf-forsikring/"
data_interim         = proj + "data/interim/"
fig                  = proj + "fig/"

raw                  = cf_space + "raw/"
processed            = cf_space + "processed/cf-forsikring/"
verify               = cf_space + "verify/"

s2s_forecast_6hourly          = raw + "s2s/mars/ecmwf/forecast/sfc/6hourly/"
s2s_forecast_daily            = processed + "s2s/ecmwf/forecast/daily/values/"
s2s_forecast_daily_smooth     = processed + "s2s/ecmwf/forecast/daily/values_smooth/"
s2s_forecast_daily_anomaly    = processed + "s2s/ecmwf/forecast/daily/anomaly/"
s2s_hindcast_6hourly          = raw + "s2s/mars/ecmwf/hindcast/sfc/6hourly/"
s2s_hindcast_daily            = processed + "s2s/ecmwf/hindcast/daily/values/"
s2s_hindcast_daily_smooth     = processed + "s2s/ecmwf/hindcast/daily/values_smooth/"
s2s_hindcast_daily_clim       = processed + "s2s/ecmwf/hindcast/daily/climatology/"
s2s_hindcast_daily_percentile = processed + "s2s/ecmwf/hindcast/daily/percentile/values_smooth/"

era5_6hourly                    = raw + "era5/6hourly/"
era5_daily                      = processed + "era5/continuous-format/daily/"
era5_s2s_forecast_daily         = processed + "era5/s2s-model-format/forecast/daily/values/"
era5_s2s_forecast_daily_smooth  = processed + "era5/s2s-model-format/forecast/daily/values_smooth/"
era5_s2s_forecast_daily_clim    = processed + "era5/s2s-model-format/forecast/daily/climatology/"
era5_s2s_forecast_daily_anomaly = processed + "era5/s2s-model-format/forecast/daily/anomaly/"
era5_s2s_hindcast_daily         = processed + "era5/s2s-model-format/hindcast/daily/"

seasonal_hindcast                 = raw + "seasonal/ecmwf/monthly/hindcast/"
seasonal_forecast                 = raw + "seasonal/ecmwf/monthly/forecast/"
seasonal_hindcast_monthly         = processed + "seasonal/ecmwf/monthly/hindcast/values/"
seasonal_forecast_monthly         = processed + "seasonal/ecmwf/monthly/forecast/values/"
seasonal_hindcast_monthly_clim    = processed + "seasonal/ecmwf/monthly/hindcast/climatology/"
seasonal_forecast_monthly_anomaly = processed + "seasonal/ecmwf/monthly/forecast/anomaly/"

era5_monthly                           = raw + "era5/monthly/"
era5_seasonal_forecast_monthly         = processed + "era5/seasonal-model-format/monthly/forecast/values/"
era5_seasonal_hindcast_monthly         = processed + "era5/seasonal-model-format/monthly/hindcast/values/"
era5_seasonal_forecast_monthly_clim    = processed + "era5/seasonal-model-format/monthly/forecast/climatology/"
era5_seasonal_forecast_monthly_anomaly = processed + "era5/seasonal-model-format/monthly/forecast/anomaly/"

verify_s2s_forecast_daily        = verify + "s2s/ecmwf/daily/forecast/"
verify_seasonal_forecast_monthly = verify + "seasonal/ecmwf/monthly/forecast/" 


#era5_forecast_daily_binary          = processed + "era5/model-format/forecast/daily/binary/"
#era5_forecast_clim_binary           = processed + "era5/model-format/forecast/climatology/binary/"
#era5_forecast_pers                  = processed + "era5/model-format/forecast/persistence/values/"
#era5_forecast_pers_binary           = processed + "era5/model-format/forecast/persistence/binary/"
#era5_hindcast_percentile            = processed + "era5/model-format/hindcast/percentile/"
#era5_cont_percentile                = processed + "era5/continuous-format/percentile/"
#s2s_forecast_daily_binary = processed + "ecmwf/forecast/daily/binary/"
#s2s_hindcast_percentile   = processed + "ecmwf/hindcast/percentile/"


dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "processed":processed,
        "s2s_forecast_6hourly":s2s_forecast_6hourly,
        "s2s_forecast_daily":s2s_forecast_daily,
        "s2s_forecast_daily_smooth":s2s_forecast_daily_smooth,
        "s2s_forecast_daily_anomaly":s2s_forecast_daily_anomaly,
        "s2s_hindcast_6hourly":s2s_hindcast_6hourly,
        "s2s_hindcast_daily":s2s_hindcast_daily,
        "s2s_hindcast_daily_smooth":s2s_hindcast_daily_smooth,
        "s2s_hindcast_daily_clim":s2s_hindcast_daily_clim,
        "s2s_hindcast_daily_percentile":s2s_hindcast_daily_percentile,
        "era5_6hourly":era5_6hourly,
	"era5_daily":era5_daily,
        "era5_monthly":era5_monthly,
        "era5_s2s_forecast_daily":era5_s2s_forecast_daily,
        "era5_s2s_forecast_daily_smooth":era5_s2s_forecast_daily_smooth,
        "era5_s2s_forecast_daily_clim":era5_s2s_forecast_daily_clim,
        "era5_s2s_forecast_daily_anomaly":era5_s2s_forecast_daily_anomaly,
        "era5_s2s_hindcast_daily":era5_s2s_hindcast_daily,        
        "seasonal_hindcast":seasonal_hindcast,
        "seasonal_forecast":seasonal_forecast,
        "seasonal_hindcast_monthly":seasonal_hindcast_monthly,
        "seasonal_forecast_monthly":seasonal_forecast_monthly,
        "seasonal_hindcast_monthly_clim":seasonal_hindcast_monthly_clim,
        "seasonal_forecast_monthly_anomaly":seasonal_forecast_monthly_anomaly,
        "era5_seasonal_forecast_monthly":era5_seasonal_forecast_monthly,
        "era5_seasonal_hindcast_monthly":era5_seasonal_hindcast_monthly,
        "era5_seasonal_forecast_monthly_clim":era5_seasonal_forecast_monthly_clim,
        "era5_seasonal_forecast_monthly_anomaly":era5_seasonal_forecast_monthly_anomaly,
        "verify_s2s_forecast_daily":verify_s2s_forecast_daily,
        "verify_seasonal_forecast_monthly":verify_seasonal_forecast_monthly
}        
