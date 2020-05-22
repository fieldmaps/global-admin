import csv
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

cwd = Path(__file__).parent
lookup_input = '../1_admin_attributes/2_merge_sources/wld.xlsx'
na_values = ['', '#N/A']


def get_converters():
    res = {}
    items = ['name1', 'name2', 'name3', 'namealt',
             'type1', 'typealt', 'id_govt', 'id_ocha']
    for lvl in range(6):
        for item in items:
            res[f'{item}_{lvl}'] = str
    return res


def add_govt(code, level):
    columns = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5', 'geometry']
    input = (cwd / f'../0_data_inputs/boundaries/govt/{code}.gpkg').resolve()
    output = (cwd / f'00_inputs/{code}.gpkg').resolve()
    layer = f'{code}_adm{level}'
    gdf = gpd.read_file(input)
    if gdf.crs['init'] != 'epsg:4326':
        raise ValueError('Dataframe does not have projection of WGS84')
    for lvl in range(level + 1):
        join = db[f'adm{lvl}'].filter(items=[f'id_{lvl}', f'id_govt_{lvl}'])
        join = join[join[f'id_{lvl}'].str.contains(code.upper(), na=False)]
        gdf = gdf.merge(join, how='outer', on=f'id_govt_{lvl}',
                        validate='many_to_one')
    gdf = gdf.filter(items=columns)
    gdf = gdf.sort_values(by=list(gdf.columns[:-1]))
    if gdf.isna().any(axis=None):
        raise ValueError('Dataframe contains NaN values')
    gdf.to_file(output, layer=layer, driver='GPKG')


db = {}
print('Loading Global Admin xlsx...')
sheets = pd.ExcelFile((cwd / lookup_input).resolve())
print('Global Admin xlsx loaded')
for sheet in sheets.sheet_names:
    db[sheet] = sheets.parse(sheet_name=sheet, converters=get_converters(),
                             na_values=na_values, keep_default_na=False)
print('Global Admin xlsx parsed')

input_path = (cwd / '../data.csv').resolve()
for index, row in pd.read_csv(input_path).iterrows():
    code = row['alpha_3'].lower()
    level = int(row['admin_level_full'])
    if row['url'] is np.nan or row['url'].startswith('https://data.humdata.org'):
        continue
    print(code)
    add_govt(code, level)
