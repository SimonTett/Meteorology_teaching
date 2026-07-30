# retrieve SYNOP messages and then plot them.
# plot_synops --fontsize 13 --thin 125 --papersize A4 --output figures/now.png
# plot_synops --fontsize 13 --thin 125 --papersize A4 --output figures/yesterday.png --date "2024-09-26 07"


from __future__ import annotations
import matplotlib

from metlib import my_logger

matplotlib.use("Agg") # headless matplotlib
import pathlib
import typing
import pandas as pd
import metlib

cache_dir = metlib.cache_dir
pd.options.mode.copy_on_write = True

typ_flt_int = typing.Union[float, int]




if __name__ == '__main__':
    # code is running as a script
    # setup parser and deal with arguments
    import argparse
    parser = argparse.ArgumentParser(description='Plot SYNOP data for Great Britain and Ireland. Could be extended to other regions.')
    parser.add_argument('--date', type=pd.Timestamp,
                        help='UTC date/time to plot data for. Default is now minus 1 hour. Format is YYYY-MM-DDTHH ',
                        default=None)
    parser.add_argument('--thin', type=float, help='Thin distance in km', default=40.)
    parser.add_argument('--output', type=pathlib.Path,
                        help='Output file to save the plot to. If not specified with be constructed from date and be pdf',
                        default=None)
    parser.add_argument('--figsize', nargs=2, type=float, help='Page size for the plot. Default is A3. Do not select this and papersize',
                        default=None)
    parser.add_argument('--papersize',type=str,choices=metlib.size_lookup.keys(),help=f'Specify paper size. Do not select this and figsize')
    parser.add_argument('--portrait',action='store_true',help='If papersize set use portrait layout')
    parser.add_argument('--region', nargs=4, type=float,
                        help='Region (long0,long1,lat0,lat1) to plot in degrees. Default is GB + Ireland. ',
                        default=(-11., 2., 49.0, 61.5))  # from Guernsey to Shetland, W-Ireland to E-England
    parser.add_argument('--use_midas_csv', action='store_true',
                        help='Use open-midas csv files. They should already have been downloaded from BADC. ')
    parser.add_argument('--nocache', action='store_true', help='Do not use the cache.')
    parser.add_argument('--plot_pressure', action='store_true',
                        help='Plot the pressure on the map. Will try and retrieve ERA5 data.')
    parser.add_argument('--nointeractive', action='store_true', help='Do not use an interactive backend.')
    parser.add_argument('--fontsize',type=int,default=11,help='Fontsize to use')
    parser.add_argument('--simple',action='store_true',help='Use simple station plot')
    parser.add_argument('--black',action='store_true',help='All station circle elements are black')
    parser.add_argument('--mountain',action='store_true',help='Give mountain stns higher prty when thinning')
    parser.add_argument('--priority_stations',type=str,help='Comma separated list of stations to give priority to')
    parser.add_argument('--pressure_labels',help='Label the pressure values',
                        action=argparse.BooleanOptionalAction,default=True)
    args = parser.parse_args()
    if args.date is None:
        date = pd.Timestamp.utcnow() - pd.Timedelta(1, 'h')
    else:
        date = pd.Timestamp(args.date, tz='UTC')

    if args.figsize and args.papersize:
        raise ValueError('Do not specify papersize and figsize')
    figsize = metlib.size_lookup['A4']
    if args.papersize is not None:
        figsize=metlib.size_lookup[args.papersize]
        if args.portrait:
            figsize=tuple(figsize[::-1])
    if args.figsize is not None:
        figsize=args.figsize
    save_file = args.output
    if save_file is None:
        save_file = date.strftime("station_plot_%Y%m%d_%H.pdf")

    if not args.nointeractive:
        backends_to_try = ['QtAgg','TkAgg']
        for backend in backends_to_try:
            try:
                matplotlib.use(backend)
                print("Using backend ", backend)
                break
            except ImportError:
                print(f'Failed to use backend {backend}')

    priority_stations = None
    if args.priority_stations:
        priority_stations = args.priority_stations.split(',')


    synops_to_plot, pressure = metlib.read_synops(date, region=args.region, nocache=args.nocache,
                                                  use_midas_csv=args.use_midas_csv,
                                                  cachier__skip_cache=args.nocache, # need to not use this routines cach
                                 get_pressure=args.plot_pressure)
    if synops_to_plot is None:
        my_logger.error('No synops to plot. Exiting')
    else:
        fig_map_synop,ax,stns = metlib.plot_synops(synops_to_plot, pressure, thin=args.thin, figsize=figsize,
                                              region=args.region,fontsize=args.fontsize,
                                              simple=args.simple,black=args.black,mountain=args.mountain,
                                              priority_stations=priority_stations,pressure_labels=args.pressure_labels)
        fig_map_synop.show()
        fig_map_synop.savefig(save_file, dpi=300, bbox_inches="tight")
