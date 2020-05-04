import os
import csv
from pathlib import Path
import geopandas as gpd
import numpy as np

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()

attributes = {
    5: ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5'],
    4: ['id_0', 'id_1', 'id_2', 'id_3', 'id_4'],
    3: ['id_0', 'id_1', 'id_2', 'id_3'],
    2: ['id_0', 'id_1', 'id_2'],
    1: ['id_0', 'id_1'],
    0: ['id_0'],
}


def final_attributes(code, level):
    input = Path(f'{cwd}/15_final_union/{code}.gpkg')
    output = Path(f'{cwd}/16_final_attributes/{code}.gpkg')
    layer = f'{code}_adm{level}'
    if os.path.isfile(input):
        gdf = gpd.read_file(input, layer=layer)
        gdf = gdf.drop('fid_2', 1)
        for attribute in attributes[level]:
            gdf[attribute] = np.where(gdf[attribute].isnull(),
                                      gdf[attribute + '_2'], gdf[attribute])
            gdf = gdf.drop(attribute + '_2', 1)
        gdf.to_file(output, layer=layer, driver="GPKG")


with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        final_attributes(code, level)
