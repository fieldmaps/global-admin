import os
import csv
from pathlib import Path
import geopandas as gpd

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()

attributes = {
    5: ['geometry', 'admin5Pcode', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    4: ['geometry', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    3: ['geometry', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    2: ['geometry', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    1: ['geometry', 'admin1Pcode', 'admin0Pcode'],
    0: ['geometry', 'admin0Pcode'],
}


def final_higher(code, level):
    input = Path(f'{cwd}/21_final_higher/{code}.gpkg')
    output = Path(f'{cwd}/22_final_higher_attr/{code}.gpkg')
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
