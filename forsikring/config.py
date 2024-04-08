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

s2s_forecast_6hourly                = raw + "s2s/mars/ecmwf/forecast/sfc/6hourly/"
s2s_forecast_6hourly_student        = raw + "s2s/mars/ecmwf/forecast/sfc/6hourly_student/"
s2s_forecast_daily                  = processed + "s2s/ecmwf/forecast/daily/values/"
s2s_forecast_daily_student          = processed + "s2s/ecmwf/forecast/daily/student/values/"
s2s_forecast_daily_student_combined = processed + "s2s/ecmwf/forecast/daily/student/combined/"
s2s_forecast_daily_smooth           = processed + "s2s/ecmwf/forecast/daily/values_smooth/"
s2s_forecast_daily_anomaly          = processed + "s2s/ecmwf/forecast/daily/anomaly_smooth/"
s2s_forecast_daily_probability      = processed + "s2s/ecmwf/forecast/daily/probability_smooth/"
s2s_forecast_weekly                 = processed + "s2s/ecmwf/forecast/weekly/values/"
s2s_forecast_weekly_anomaly         = processed + "s2s/ecmwf/forecast/weekly/anomaly_smooth/"
s2s_forecast_weekly_probability     = processed + "s2s/ecmwf/forecast/weekly/probability_smooth/"
s2s_hindcast_6hourly                = raw + "s2s/mars/ecmwf/hindcast/sfc/6hourly/"
s2s_hindcast_daily                  = processed + "s2s/ecmwf/hindcast/daily/values/"
s2s_hindcast_daily_climatology      = processed + "s2s/ecmwf/hindcast/daily/climatology/values_smooth/"
s2s_hindcast_daily_quantile         = processed + "s2s/ecmwf/hindcast/daily/quantile/values_smooth/"
s2s_hindcast_weekly                 = processed + "s2s/ecmwf/hindcast/weekly/values/"

era5_6hourly                         = raw + "era5/6hourly/"
era5_daily                           = processed + "era5/continuous-format/daily/"
era5_daily_student                   = processed + "era5/continuous-format/daily/student/"
era5_forecast_daily                  = processed + "era5/s2s-model-format/forecast/daily/values/"
era5_forecast_daily_student          = processed + "era5/s2s-model-format/forecast/daily/student/values/"
era5_forecast_daily_student_combined = processed + "era5/s2s-model-format/forecast/daily/student/combined/"
era5_forecast_daily_smooth           = processed + "era5/s2s-model-format/forecast/daily/values_smooth/"
era5_forecast_daily_anomaly          = processed + "era5/s2s-model-format/forecast/daily/anomaly_smooth/"
era5_forecast_daily_binary           = processed + "era5/s2s-model-format/forecast/daily/binary_smooth/"
era5_forecast_weekly                 = processed + "era5/s2s-model-format/forecast/weekly/values/"
era5_forecast_weekly_anomaly         = processed + "era5/s2s-model-format/forecast/weekly/anomaly_smooth/"
era5_forecast_weekly_binary          = processed + "era5/s2s-model-format/forecast/weekly/binary_smooth/"
era5_hindcast_daily                  = processed + "era5/s2s-model-format/hindcast/daily/values/"
era5_hindcast_daily_quantile         = processed + "era5/s2s-model-format/hindcast/daily/quantile/values_smooth/"
era5_hindcast_daily_climatology      = processed + "era5/s2s-model-format/hindcast/daily/climatology/values_smooth/"
era5_hindcast_weekly_quantile        = processed + "era5/s2s-model-format/hindcast/weekly/quantile/values_smooth/"
era5_hindcast_weekly_climatology     = processed + "era5/s2s-model-format/hindcast/weekly/climatology/values_smooth/"

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


dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "processed":processed,
        "s2s_forecast_6hourly":s2s_forecast_6hourly,
        "s2s_forecast_6hourly_student":s2s_forecast_6hourly_student,
        "s2s_forecast_daily":s2s_forecast_daily,
        "s2s_forecast_daily_smooth":s2s_forecast_daily_smooth,
        "s2s_forecast_daily_anomaly":s2s_forecast_daily_anomaly,
	"s2s_forecast_daily_probability":s2s_forecast_daily_probability,
        "s2s_forecast_daily_student":s2s_forecast_daily_student,
        "s2s_forecast_daily_student_combined":s2s_forecast_daily_student_combined,
        "s2s_forecast_weekly":s2s_forecast_weekly,
        "s2s_forecast_weekly_anomaly":s2s_forecast_weekly_anomaly,
        "s2s_forecast_weekly_probability":s2s_forecast_weekly_probability,        
        "s2s_hindcast_6hourly":s2s_hindcast_6hourly,
        "s2s_hindcast_daily":s2s_hindcast_daily,
        "s2s_hindcast_daily_climatology":s2s_hindcast_daily_climatology,
        "s2s_hindcast_daily_quantile":s2s_hindcast_daily_quantile,
        "s2s_hindcast_weekly":s2s_hindcast_weekly,
        "era5_6hourly":era5_6hourly,
	"era5_daily":era5_daily,
        "era5_daily_student":era5_daily_student,
        "era5_monthly":era5_monthly,
        "era5_forecast_daily":era5_forecast_daily,
        "era5_forecast_daily_student":era5_forecast_daily_student,
        "era5_forecast_daily_student_combined":era5_forecast_daily_student_combined,
        "era5_forecast_daily_smooth":era5_forecast_daily_smooth,
        "era5_forecast_daily_anomaly":era5_forecast_daily_anomaly,
        "era5_forecast_daily_binary":era5_forecast_daily_binary,
        "era5_forecast_weekly":era5_forecast_weekly,
        "era5_forecast_weekly_anomaly":era5_forecast_weekly_anomaly,
        "era5_forecast_weekly_binary":era5_forecast_weekly_binary,        
        "era5_hindcast_daily":era5_hindcast_daily,
        "era5_hindcast_daily_quantile":era5_hindcast_daily_quantile,
        "era5_hindcast_daily_climatology":era5_hindcast_daily_climatology,
        "era5_hindcast_weekly_quantile":era5_hindcast_weekly_quantile,
        "era5_hindcast_weekly_climatology":era5_hindcast_weekly_climatology,        
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
