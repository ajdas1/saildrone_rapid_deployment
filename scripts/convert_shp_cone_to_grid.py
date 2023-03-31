


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
outdir = "/Users/asavarin/Desktop/saildrone_rapid_deployment/data/nc/"

forecast_time = [0, 12, 24, 36, 48 , 60, 72, 90, 120]

for directory in data_dirs:
    fname = directory.split(os.sep)[-1]

    fls = [fl for fl in os.listdir(directory) if (".shp" in fl) and (".xml" not in fl)]
    storm_number = fname[2:4]
    storm_year = fname[4:8]
    if int(storm_year) == 2022:
        print(fname)
        fl_cone = [fl for fl in fls if "_pgn.shp" in fl][0]
        fl_point = [fl for fl in fls if "_pts.shp" in fl][0]
        datafile_cone = f"{directory}/{fl_cone}"
        datafile_point = f"{directory}/{fl_point}"
        lon_point = np.zeros((9)) * np.nan
        lat_point = np.zeros((9)) * np.nan
        if os.path.isfile(datafile_cone):
            cone = geopandas.read_file(datafile_cone)
            cone = cone.to_crs(4326)

            cone_overlap_grid = np.zeros(grid["lon"].shape)

            for point in gom_points:
                if cone.contains(point)[0]:
                    lonval = point.x
                    latval = point.y
                    lonidx = list(coords["lon"]).index(lonval)
                    latidx = list(coords["lat"]).index(latval)
                    cone_overlap_grid[latidx, lonidx] = 1


            # if np.nansum(cone_overlap_grid) > 0:
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



            outfile = outdir + datafile_cone.split(os.sep)[-1].split(".")[0][:-4] + ".nc"

            ncfile = Dataset(outfile, "w")

            ncfile.createDimension("time", None)
            ncfile.createDimension("lon", len(coords["lon"]))
            ncfile.createDimension("lat", len(coords["lat"]))
            ncfile.createDimension("fcst_time", len(forecast_time))

            v0 = ncfile.createVariable("lon", "f8", ("lon"))
            v0.units = "degrees_east"
            v0[:] = coords["lon"]

            v0 = ncfile.createVariable("lat", "f8", ("lat"))
            v0.units = "degrees_north"
            v0[:] = coords["lat"]

            v0 = ncfile.createVariable("fcst_time", "f8", ("fcst_time"))
            v0.units = "hours since " + adv_time.strftime("%Y-%m-%d %H:%M UTC")
            v0[:] = forecast_time

            v1 = ncfile.createVariable("cone", "f8", ("time", "lat", "lon"))
            v1.units = "/"
            v1[0, :] = cone_overlap_grid

            v1 = ncfile.createVariable("center_lon", "f8", ("time", "fcst_time"))
            v1.units = "degrees_east"
            v1[0, :] = np.ma.masked_invalid(lon_point)

            v2 = ncfile.createVariable("center_lat", "f8", ("time", "fcst_time"))
            v2.units = "degrees_north"
            v2[0, :] = np.ma.masked_invalid(lat_point)
            ncfile.close()




# import matplotlib.pyplot as plt

# fig = plt.figure()
# ax = fig.add_subplot(111)
# # gom_points.plot(ax=ax)
# cone.plot(ax=ax, markersize=1, facecolor="none")
# points.plot(ax=ax)
# # ax.contourf(grid["lon"], grid["lat"], cone_overlap_grid, levels=[0.5, 1.5])
# plt.savefig("test.png")
# plt.close("all")