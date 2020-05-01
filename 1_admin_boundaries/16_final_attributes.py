import os
import csv
from pathlib import Path
import geopandas as gpd
import numpy as np

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()

levels = {
    '5': ['admin5Pcode', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '4': ['admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '3': ['admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '2': ['admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '1': ['admin1Pcode', 'admin0Pcode'],
    '0': ['admin0Pcode'],
}


def final_attributes(code, level):
    input = Path(f'{cwd}/15_final_union/{code}.gpkg')
    output = Path(f'{cwd}/16_final_attributes/{code}.gpkg')
    layer = f'{code}_adm{level}'
    if os.path.isfile(input):
        gdf = gpd.read_file(input, layer=layer)
        gdf = gdf.drop('fid_2', 1)
        for attribute in levels[level]:
            gdf[attribute] = np.where(gdf[attribute].isnull(),
                                      gdf[attribute + '_2'], gdf[attribute])
            gdf = gdf.drop(attribute + '_2', 1)
        gdf.to_file(output, layer=layer, driver="GPKG")


with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = row['admin_level_full']
        final_attributes(code, level)
