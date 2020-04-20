import os
import csv
import json
import shutil
from pathlib import Path
import geopandas as gpd


def final_higher(code, level):
    input = Path('{0}/tmp/20_final_higher/{1}.gpkg'.format(cwd, code))
    output = Path('{0}/tmp/21_final_higher_attr/{1}.gpkg'.format(cwd, code))
    if os.path.isfile(input):
        for l in levels[level]:
            layer = '{0}_adm{1}'.format(code, l)
            gdf = gpd.read_file(input, layer=layer)
            gdf = gdf[gdf.columns[gdf.columns.isin(attributes[l])]]
            gdf.to_file(output, layer=layer, driver="GPKG")


cwd = os.getcwd()
levels = {
    '5': ['5', '4', '3', '2', '1', '0'],
    '4': ['4', '3', '2', '1', '0'],
    '3': ['3', '2', '1', '0'],
    '2': ['2', '1', '0'],
    '1': ['1', '0'],
    '0': ['0'],
}
attributes = {
    '5': ['geometry', 'admin5Pcode', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '4': ['geometry', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '3': ['geometry', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '2': ['geometry', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '1': ['geometry', 'admin1Pcode', 'admin0Pcode'],
    '0': ['geometry', 'admin0Pcode'],
}

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        final_higher(code, level)
