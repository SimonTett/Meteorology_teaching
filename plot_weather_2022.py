# Plot the weather during the heatwave of 2022.

import pathlib

import pandas as pd
import metlib
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

date = pd.Timestamp('2022-07-19 15')
region = (-6., 3., 49.0, 59.)
sub_region = (-3,3,50,54)
save_dir=pathlib.Path('plots_2022')
save_dir.mkdir(exist_ok=True,parents=True)
proj = ccrs.AlbersEqualArea(central_longitude=0, central_latitude=54, false_easting=400000,
                            false_northing=-100000)  # UK projection

with plt.ioff():
    for date in pd.date_range('2022-07-19 00',periods=31,freq='1h',tz='UTC'):
        figname=f'weather_{date.strftime("%Y%m%d_%H")}'
        synops_to_plot, pressure = metlib.read_synops(date, region=region, get_pressure=True)#,use_midas_csv=True)
        if synops_to_plot is None:
            print(f'No synops to plot for {date}. Skipping')
            continue
        # rename src_name to srce_name . TODO move this change into read_synops
        synops_to_plot= synops_to_plot.rename(columns=dict(src_name='srce_name'))
        max_idx= synops_to_plot.air_temperature.idxmax()
        max_name = synops_to_plot.loc[max_idx].srce_name
        # find min DP
        min_idx = synops_to_plot.dewpoint.idxmin()
        min_name = synops_to_plot.loc[min_idx].srce_name

        fig, axes = plt.subplots(1, 2, figsize=(13,7), subplot_kw=dict(projection=proj), clear=True,
                               layout='tight', num=figname)
        fontsize=12
        for ax,rgn in zip(axes,[region,sub_region]):
            ax.set_extent(rgn, crs=ccrs.PlateCarree())
            ax.coastlines(color='grey', linewidth=1)
            ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, color='grey',
                         xlabel_style=dict(size=fontsize), ylabel_style=dict(size=fontsize))
        fig_map_synop,ax,stns = metlib.plot_synops(synops_to_plot, pressure, thin=125., figsize=(16,7),ax=axes[0],
                                                      region=region,fontsize=12,
                                                   priority_stations=[max_name,'Edinburgh',min_name],figname=figname)
        figname2=figname+'_sub'
        fig_map_sub,ax,stns = metlib.plot_synops(synops_to_plot, pressure, thin=35., figsize=(16,7),ax=axes[1],
                                                      region=sub_region,fontsize=12,priority_stations=['Coningsby','ST JAMES PARK','SCAMPTON'],
                                                 figname=figname2,simple=True)
        print('Max temperature:',synops_to_plot.air_temperature.max(),'at',max_name)
        print('Min dewpoint:', synops_to_plot.dewpoint.min(), 'at', min_name)
        #fig_map_synop.show()
        fig_map_synop.savefig(save_dir/f'{figname}.png',dpi=300,bbox_inches='tight')
        plt.close(fig_map_synop)

    # plot CET -- daily max and min from 1st July on.



