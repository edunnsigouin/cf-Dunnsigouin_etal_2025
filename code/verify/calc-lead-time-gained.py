"""
calculates the lead-time gained by increasing spatial scale for a given
forecast skill based off of lead-time vs spatial scale fss data.
"""

import numpy    as np
import xarray   as xr
from forsikring import misc,s2s,verify,config
from matplotlib import pyplot as plt

# INPUT -----------------------------------------------
score_flag               = 'fss'
time_flag                = 'weekly'                   # daily or weekly
variable                 = 'tp24'                   # tp24,rn24,mx24rn6,mx24tp6,mx24tpr
domain                   = 'europe'                 # europe or norway only? 
first_forecast_date      = '20210104'               # first initialization date of forecast (either a monday or thursday)
number_forecasts         = 104                      # number of forecasts
season                   = 'annual'                 # pick forecasts in specific season (djf,mam,jja,son,annual)
pval                     = 0.9
grids                    = ['0.25x0.25','0.5x0.5']
write2file               = True
# -----------------------------------------------------    

misc.tic()

# define stuff
forecast_dates          = s2s.get_forecast_dates(first_forecast_date,number_forecasts,season).strftime('%Y-%m-%d')
path_in                 = config.dirs['verify_s2s_forecast_daily']
path_out                = config.dirs['verify_s2s_forecast_daily']
if score_flag == 'fss':
    prefix_in  = score_flag + '_' + variable + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]
    prefix_out = 'ltg_' + score_flag + '_' + variable + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]
elif score_flag == 'fbss':
    prefix_in  = score_flag + '_' + variable + '_pval' + str(pval) + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]
    prefix_out = 'ltg_' + score_flag + '_' + variable + '_pval' + str(pval) + '_' + time_flag + '_' + domain + '_' + season + '_' + forecast_dates[0] + '_' + forecast_dates[-1]
    
if len(grids) == 2:
    filename_in  = prefix_in + '.nc'
    filename_out = prefix_out + '.nc'
else:
    filename_in  = prefix_in + '_' + grids[0] + '.nc'
    filename_out = prefix_out + '_' + grids[0] + '.nc'
    
# read score data
score = xr.open_dataset(path_in + filename_in)
time  = score.time.values

# interpolate lead time dimension
score_interp = score[score_flag].interp(time=np.arange(time[0],time[-1]+0.2,0.2))
time_interp  = score_interp.time
box_size     = score_interp.box_size

# calculate lead time gained
lead_time_gained      = score_interp.copy()
lead_time_gained      = lead_time_gained.rename({'time':'time_interp'})
lead_time_gained      = lead_time_gained.rename('lead_time_gained')
lead_time_gained[:,:] = 0.0
for bs in range(1,box_size.size):
    for t in range(0,time_interp.size):
        temp = np.absolute(score_interp[bs,t].values-score_interp[0,:].values)
        if time_interp[np.nanargmin(temp)].values == 1.0: # where there is no skill equivalent at grid resolution
            lead_time_gained[bs,t] = np.nan
        else:
            lead_time_gained[bs,t] = time_interp[t].values - time_interp[np.nanargmin(temp)].values

# calculate significance of score            
sig = s2s.mask_significant_values_from_bootstrap(score[score_flag + '_bootstrap'],0.05)

# calculate accuracy not acheivable at the grid score
max_skill = s2s.mask_skill_values(lead_time_gained)
max_skill = max_skill.rename('max_skill')

# set ltg values to nan where score not-significant
time_interp_int = lead_time_gained.time_interp.astype('int')
for bs in range(1,box_size.size):
    index1                              = time[np.where(sig[bs,:] == 1.0)[0]]
    index2                              = np.where(time_interp_int == index1[0])[0][0]-2
    lead_time_gained[bs,index2:]        = np.nan

# merge all variables
output = xr.merge([score,lead_time_gained,sig,max_skill])

# generalize score names
output = output.rename({score_flag:'score'})
output = output.rename({score_flag + '_bootstrap':'score_bootstrap'})

# change units of weekly ltg to days from weeks.
if time_flag == 'weekly':
    output['lead_time_gained'] = output['lead_time_gained']*7

# write to file
if write2file: output.to_netcdf(path_out+filename_out) 

misc.toc()
