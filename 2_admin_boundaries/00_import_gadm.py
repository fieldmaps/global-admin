import csv
from pathlib import Path
import pandas as pd
import geopandas as gpd

cwd = Path(__file__).parent
lookup_input = '../1_admin_attributes/2_merge_sources/wld.xlsx'
na_values = ['', '#N/A']
re_filter = r'^[Ww]ater\s?[Bb]ody|[Ll]ake$'


def add_gadm(code, level):
    columns = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5', 'geometry']
    input = (cwd / f'00_inputs/gadm/GID_0_{code}.gpkg').resolve()
    output = (cwd / f'00_inputs/{code}.gpkg').resolve()
    layer = f'{code}_adm{level}'
    gdf = gpd.read_file(input)
    gdf = gdf[~gdf['ENGTYPE_1'].str.contains(re_filter, na=False)]
    gdf = gdf[~gdf['ENGTYPE_2'].str.contains(re_filter, na=False)]
    gdf = gdf[~gdf['ENGTYPE_3'].str.contains(re_filter, na=False)]
    gdf = gdf[~gdf['ENGTYPE_4'].str.contains(re_filter, na=False)]
    gdf = gdf[~gdf['ENGTYPE_5'].str.contains(re_filter, na=False)]
    for lvl in range(level + 1):
        renamed = {f'id_gadm_{lvl}': f'GID_{lvl}'}
        join = db[f'adm{lvl}'].filter(items=[f'id_{lvl}', f'id_gadm_{lvl}'])
        join = join[join[f'id_{lvl}'].str.contains(code.upper(), na=False)]
        join = join.rename(columns=renamed)
        gdf = gdf.merge(join, how='outer', on=f'GID_{lvl}',
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
    db[sheet] = sheets.parse(sheet_name=sheet, na_values=na_values,
                             keep_default_na=False)
print('Global Admin xlsx parsed')

with open((cwd / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        if row['source'] in ['GADM', '']:
            print(code)
            add_gadm(code, level)
