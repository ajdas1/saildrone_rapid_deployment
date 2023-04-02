import numpy as np
import os
import subprocess



datadir = "/Users/asavarin/Desktop/saildrone_rapid_deployment/data/nc/"
fcst_datadir = "/Users/asavarin/Desktop/saildrone_rapid_deployment/data/nc/individual_fcsts/"


fls = sorted([f"{fcst_datadir}{fl}" for fl in os.listdir(fcst_datadir) if (".nc" in fl)])

storm_year = []
forecast = []
for fl in fls:
    storm_year.append(fl.split(os.sep)[-1][2:8])
    forecast.append(fl.split(os.sep)[-1][9:12])

storm_year_sets = np.unique(storm_year)
fcst_files = []
storm_year_set = []
for sy in storm_year_sets:
    fcst_files.append(sorted([fl for fl in fls if sy in fl]))
    storm_year_set.append(sy)

for num, fcsts in enumerate(fcst_files):

    command = ["ncrcat"] + fcsts + [f"{datadir}al{storm_year_set[num]}_forecasts.nc"]
    subprocess.run(command)



