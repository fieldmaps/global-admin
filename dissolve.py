import os
import csv
from pathlib import Path
import geopandas as gpd

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()

gdf = gpd.read_file(
    '/Users/maxmalynowsky/Downloads/tza_admbnda_adm3_20181019/tza_admbnda_adm3_20181019.shp')
gdf = gdf.dissolve(by='ADM0_PCODE')
gdf.to_file('/Users/maxmalynowsky/Downloads/tza.shp')
