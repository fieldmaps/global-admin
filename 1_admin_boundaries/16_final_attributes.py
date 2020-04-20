import os
import csv
import json
import shutil
from pathlib import Path
import geopandas as gpd
import numpy as np


def final_attributes(code, level):
    input = Path('{0}/tmp/15_final_union/{1}.gpkg'.format(cwd, code))
    output = Path('{0}/tmp/16_final_attributes/{1}.gpkg'.format(cwd, code))
    layer = '{0}_adm{1}'.format(code, level)
    if os.path.isfile(input):
        gdf = gpd.read_file(input, layer=layer)
        gdf = gdf.drop('fid_2', 1)
        for attribute in levels[level]:
            gdf[attribute] = np.where(gdf[attribute].isnull(),
                                      gdf[attribute + '_2'], gdf[attribute])
            gdf = gdf.drop(attribute + '_2', 1)
        gdf.to_file(output, layer=layer, driver="GPKG")


cwd = os.getcwd()
levels = {
    '5': ['admin5Pcode', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '4': ['admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '3': ['admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '2': ['admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '1': ['admin1Pcode', 'admin0Pcode'],
    '0': ['admin0Pcode'],
}

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        final_attributes(code, level)
