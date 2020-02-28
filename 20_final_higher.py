import os
import csv
import json
import shutil
from pathlib import Path
import geopandas as gpd


def final_higher(code, level):
    input = Path('{0}/tmp/19_final_holes/{1}.gpkg'.format(cwd, code))
    output = Path('{0}/tmp/20_final_higher/{1}.gpkg'.format(cwd, code))
    shutil.copyfile(input, output)
    gdf = gpd.read_file(input)
    if 'admin4Pcode' in gdf.columns:
        dis = gdf.dissolve(by='admin3Pcode')
        dis = dis[dis.columns[dis.columns.isin(
            ['geometry', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'])]]
        dis.to_file(output, layer=code + '_adm3', driver="GPKG")
    if 'admin3Pcode' in gdf.columns:
        dis = gdf.dissolve(by='admin2Pcode')
        dis = dis[dis.columns[dis.columns.isin(
            ['geometry', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'])]]
        dis.to_file(output, layer=code + '_adm2', driver="GPKG")
    if 'admin2Pcode' in gdf.columns:
        dis = gdf.dissolve(by='admin1Pcode')
        dis = dis[dis.columns[dis.columns.isin(
            ['geometry', 'admin1Pcode', 'admin0Pcode'])]]
        dis.to_file(output, layer=code + '_adm1', driver="GPKG")
    if 'admin1Pcode' in gdf.columns:
        dis = gdf.dissolve(by='admin0Pcode')
        dis = dis[dis.columns[dis.columns.isin(['geometry', 'admin0Pcode'])]]
        dis.to_file(output, layer=code + '_adm0', driver="GPKG")


cwd = os.getcwd()

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        if code in ['mrt', 'uga']:
            final_higher(code, level)
