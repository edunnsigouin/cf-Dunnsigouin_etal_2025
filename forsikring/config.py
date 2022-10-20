"""
hard coded paths in cf-forsikring
"""

cf_space            = "/nird/projects/NS9873K/etdu/"
proj                = "/nird/home/edu061/cf-forsikring/"
data_interim        = proj + "data/interim/"
fig                 = proj + "fig/"
processed           = cf_space + "processed/"
raw                 = cf_space + "raw/"
raw_hindcast        = raw + "s2s/mars/ecmwf/hindcast/sfc/"
raw_forecast        = raw + "s2s/mars/ecmwf/forecast/sfc/"
processed_hindcast  = processed + "s2s/mars/ecmwf/hindcast/sfc/"
processed_forecast  = processed + "s2s/mars/ecmwf/forecast/sfc/"
era5                = raw + "era5/0.25x0.25_daily_europe_nc/"

dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "processed":processed,
        "raw_hindcast":raw_hindcast,
        "raw_forecast":raw_forecast,
        "processed_hindcast":processed_hindcast,
        "processed_forecast":processed_forecast,
        "era5":era5
}        
