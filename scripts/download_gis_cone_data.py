import os
import requests
import subprocess
import urllib

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from netCDF4 import Dataset

gis_datadir = "/Users/asavarin/Desktop/saildrone_rapid_deployment/data/gis/"

# url_base = "https://www.nhc.noaa.gov/gis/archive_forecast_results.php?id=al01&year=2022"
url_base = "https://www.nhc.noaa.gov/gis/forecast/archive/"


page = requests.get(url_base).text
soup = BeautifulSoup(page, "html.parser")
gis_records = [f"{url_base}/{node.get('href')}" for node in soup.find_all("a")]
cone_records = sorted([
    fl for fl in gis_records
    if ("_5day_" in fl)
    and not ("A.zip" in fl)
    and not ("a.zip" in fl)
    and not ("B.zip" in fl)
    and not ("b.zip" in fl)
    and not ("latest.zip" in fl)
    and ("al" in fl)
])

for num, record in enumerate(cone_records):
    filename = record.split("/")[-1]
    if not os.path.isfile(f"{gis_datadir}{filename}"):
        print(num+1, filename)
        try:
            urllib.request.urlretrieve(record, f"{gis_datadir}{filename}")

        except urllib.error.HTTPError:
            continue


fls_to_unzip = sorted([fl for fl in os.listdir(gis_datadir) if ".zip" in fl])

for file in fls_to_unzip:
    print(file)
    unzip_command = ["unzip", f"{gis_datadir}{file}", "-d", f"{gis_datadir}{file.split('.')[0]}"]
    subprocess.run(unzip_command)
    os.remove(f"{gis_datadir}{file}")

[subprocess.run(["unzip", f"{gis_datadir}{file}", "-d", f"{gis_datadir}{file.split('.')[0]}"]) for file in fls_to_unzip]
