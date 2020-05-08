import os
import csv
from pathlib import Path
import geopandas as gpd

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()

attributes = {
    5: ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5', 'geometry'],
    4: ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'geometry'],
    3: ['id_0', 'id_1', 'id_2', 'id_3', 'geometry'],
    2: ['id_0', 'id_1', 'id_2', 'geometry'],
    1: ['id_0', 'id_1', 'geometry'],
    0: ['id_0', 'geometry'],
}


def final_higher(code, level):
    input = Path(f'{cwd}/20_final_higher/{code}.gpkg')
    output = Path(f'{cwd}/21_final_higher_attr/{code}.gpkg')
    if os.path.isfile(input):
        print(code)
        for l in range(level, -1, -1):
            layer = f'{code}_adm{l}'
            gdf = gpd.read_file(input, layer=layer)
            gdf = gdf[gdf.columns[gdf.columns.isin(attributes[l])]]
            gdf.to_file(output, layer=layer, driver="GPKG")


with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        final_higher(code, level)
