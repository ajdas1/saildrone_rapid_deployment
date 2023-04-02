


import geopandas
import gom_grid
import numpy as np
import os

from datetime import datetime
from netCDF4 import Dataset

dlon = dlat = .1
coords = gom_grid.lat_lon_coordinates(dlon=dlon, dlat=dlat)
grid = gom_grid.lat_lon_grid(dlon=dlon, dlat=dlat)
gom_points = geopandas.GeoSeries(gom_grid.lat_lon_points(dlon=dlon, dlat=dlat))


datadir = "/Users/asavarin/Desktop/saildrone_rapid_deployment/data/gis/"
data_dirs = sorted([f"{datadir}{dir}" for dir in os.listdir(datadir) if "al" in dir])
outdir = "/Users/asavarin/Desktop/saildrone_rapid_deployment/data/nc/individual_fcsts/"
wspd_dirs = sorted([f"{datadir}{dir}" for dir in os.listdir(datadir) if "wsp_120hr" in dir])

forecast_time = [0, 12, 24, 36, 48 , 60, 72, 90, 120]
percentage = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

for directory in data_dirs:
    fname = directory.split(os.sep)[-1]
    fls = [fl for fl in os.listdir(directory) if (".shp" in fl) and (".xml" not in fl)]
    storm_number = fname[2:4]
    storm_year = fname[4:8]
    if int(storm_year) == 2019:
        print(fname)
        fl_cone = [fl for fl in fls if "_pgn.shp" in fl][0]
        fl_point = [fl for fl in fls if "_pts.shp" in fl][0]
        datafile_cone = f"{directory}/{fl_cone}"
        datafile_point = f"{directory}/{fl_point}"
        lon_point = np.zeros((9)) * np.nan
        lat_point = np.zeros((9)) * np.nan

        outfile = outdir + datafile_cone.split(os.sep)[-1].split(".")[0][:-4] + ".nc"
        if not os.path.isfile(outfile):
            cone_overlap_grid = np.zeros(grid["lon"].shape)
            wspd34_overlap_grid = np.zeros(grid["lon"].shape)
            wspd50_overlap_grid = np.zeros(grid["lon"].shape)
            wspd64_overlap_grid = np.zeros(grid["lon"].shape)

            if os.path.isfile(datafile_cone):
                cone = geopandas.read_file(datafile_cone)
                cone = cone.to_crs(4326)

                cone_overlap_grid = gom_grid.mask_point_grid_in_polygon(gom_points=gom_points, polygon=cone.iloc[0].geometry, point_coordinates=coords, mask_value=1)


            if os.path.isfile(datafile_point):
                points = geopandas.read_file(datafile_point)
                for num, point in enumerate(points.geometry):
                    lon_point[num] = point.x
                    lat_point[num] = point.y

                start_time = points["ADVDATE"].loc[0]
                valid_time = points["VALIDTIME"].loc[0]
                try:
                    s_time = datetime.strptime(start_time[:8] + start_time[16:], "%I%M %p %b %d %Y")
                except ValueError:
                    s_time = datetime.strptime("0"+start_time[:7] + start_time[15:], "%I%M %p %b %d %Y")

                v_time = datetime.strptime(valid_time, "%d/%H%M")
                adv_time = s_time.replace(day=v_time.day, hour=v_time.hour, minute=v_time.minute)

                
                dir_wspd = [dir for dir in wspd_dirs if adv_time.strftime("%Y%m%d%H") in dir]
                    
                if len(dir_wspd) > 0:
                    try:
                        fl_wspd = [fl for fl in os.listdir(dir_wspd[0]) if ("wsp34knt120hr_5km.shp" in fl) and ("xml" not in fl)][0]
                        winds = geopandas.read_file(f"{dir_wspd[0]}/{fl_wspd}")
                        winds.to_crs(4326)
                        for perc in range(1, len(percentage)):
                            wspd34_overlap_grid += gom_grid.mask_point_grid_in_polygon(gom_points=gom_points, polygon=winds.iloc[perc-1].geometry, point_coordinates=coords, mask_value=perc)
                    except IndexError:
                        continue

                    try:
                        fl_wspd = [fl for fl in os.listdir(dir_wspd[0]) if ("wsp50knt120hr_5km.shp" in fl) and ("xml" not in fl)][0]
                        winds = geopandas.read_file(f"{dir_wspd[0]}/{fl_wspd}")
                        winds.to_crs(4326)
                        for perc in range(1, len(percentage)):
                            wspd50_overlap_grid += gom_grid.mask_point_grid_in_polygon(gom_points=gom_points, polygon=winds.iloc[perc-1].geometry, point_coordinates=coords, mask_value=perc)
                    except IndexError:
                        continue

                    try:
                        fl_wspd = [fl for fl in os.listdir(dir_wspd[0]) if ("wsp64knt120hr_5km.shp" in fl) and ("xml" not in fl)][0]
                        winds = geopandas.read_file(f"{dir_wspd[0]}/{fl_wspd}")
                        winds.to_crs(4326)
                        for perc in range(1, len(percentage)):
                            wspd64_overlap_grid += gom_grid.mask_point_grid_in_polygon(gom_points=gom_points, polygon=winds.iloc[perc-1].geometry, point_coordinates=coords, mask_value=perc)
                    except IndexError:
                        continue




            ncfile = Dataset(outfile, "w")

            ncfile.createDimension("time", None)
            ncfile.createDimension("lon", len(coords["lon"]))
            ncfile.createDimension("lat", len(coords["lat"]))
            ncfile.createDimension("fcst_time", len(forecast_time))
            ncfile.createDimension("probabilities", len(percentage))

            v0 = ncfile.createVariable("lon", "f8", ("lon"))
            v0.units = "degrees_east"
            v0[:] = coords["lon"]

            v0 = ncfile.createVariable("lat", "f8", ("lat"))
            v0.units = "degrees_north"
            v0[:] = coords["lat"]

            v0 = ncfile.createVariable("fcst_time", "f8", ("fcst_time"))
            v0.units = "hours since " + adv_time.strftime("%Y-%m-%d %H:%M UTC")
            v0[:] = forecast_time

            v0 = ncfile.createVariable("percentage", "f8", ("probabilities"))
            v0.units = "%"
            v0[:] = percentage

            v1 = ncfile.createVariable("center_lon", "f8", ("time", "fcst_time"))
            v1.units = "degrees_east"
            v1[0, :] = np.ma.masked_invalid(lon_point)

            v1 = ncfile.createVariable("center_lat", "f8", ("time", "fcst_time"))
            v1.units = "degrees_north"
            v1[0, :] = np.ma.masked_invalid(lat_point)

            v2 = ncfile.createVariable("cone", "f8", ("time", "lat", "lon"))
            v2.units = "/"
            v2[0, :] = cone_overlap_grid

            v2 = ncfile.createVariable("windprob_34", "f8", ("time", "lat", "lon"))
            v2.units = "category in probabilities"
            v2[0, :] = wspd34_overlap_grid

            v2 = ncfile.createVariable("windprob_50", "f8", ("time", "lat", "lon"))
            v2.units = "category in probabilities"
            v2[0, :] = wspd50_overlap_grid

            v2 = ncfile.createVariable("windprob_64", "f8", ("time", "lat", "lon"))
            v2.units = "category in probabilities"
            v2[0, :] = wspd64_overlap_grid

            ncfile.close()






# import matplotlib.pyplot as plt
# fig = plt.figure()
# ax = fig.add_subplot(111)
# f1 = ax.contourf(grid["lon"], grid["lat"], wspd34_overlap_grid, levels=(np.array(percentage)/10)+.5)
# plt.colorbar(f1)
# plt.savefig("test.png")
# plt.close("all")
