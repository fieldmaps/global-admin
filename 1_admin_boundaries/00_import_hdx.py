import csv
from pathlib import Path
import pandas as pd
import geopandas as gpd

cwd = Path(__file__).parent
lookup_input = '../1_admin_attributes/2_merge_sources/wld.xlsx'
na_values = ['', '#N/A']


def add_hdx(code, level):
    columns = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5', 'geometry']
    input = (cwd / f'../0_data_inputs/boundaries/hdx/{code}.gpkg').resolve()
    output = (cwd / f'00_inputs/{code}.gpkg').resolve()
    layer = f'{code}_adm{level}'
    gdf = gpd.read_file(input)
    for lvl in range(level + 1):
        renamed = {'id': f'id_{lvl}', 'code_ocha': f'admin{lvl}Pcode'}
        join = db[f'adm{lvl}'].filter(items=['id', 'code_ocha'])
        join = join[join.id.str.contains(code.upper(), na=False)]
        join = join.rename(columns=renamed)
        gdf = gdf.merge(join, how='outer', on=f'admin{lvl}Pcode',
                        validate='many_to_one')
    gdf = gdf.filter(items=columns)
    gdf = gdf.sort_values(by=list(gdf.columns[:-1]))
    if gdf.isna().any(axis=None):
        raise ValueError('Dataframe contains NaN values')
    gdf.to_file(output, layer=layer, driver="GPKG")


db = {}
print('Loading Global Admin xlsx...')
sheets = pd.ExcelFile((cwd / lookup_input).resolve())
print('Global Admin xlsx loaded')
for sheet in sheets.sheet_names:
    db[sheet] = sheets.parse(sheet_name=sheet, na_values=na_values,
                             keep_default_na=False)
print('Global Admin xlsx parsed')

with open((cwd / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        hdx_url = row['url'].startswith('https://data.humdata.org')
        gadm_source = row['source'] == 'GADM'
        if hdx_url and not gadm_source:
            print(code)
            add_hdx(code, level)
