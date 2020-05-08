import os
import csv
from pathlib import Path
import pandas as pd
import geopandas as gpd

cwd = Path(__file__).parent
(cwd / '24_final_export').mkdir(parents=True, exist_ok=True)

input_1 = (cwd / '23_final_merge/wld.gpkg').resolve()
input_2 = (cwd / '23_final_merge/wld_levels.gpkg').resolve()
output_1 = (cwd / '24_final_export/wld.gpkg').resolve()
output_2 = (cwd / '24_final_export/wld_levels.gpkg').resolve()

na_values = ['', '#N/A']
lookup_input = (
    cwd / '../1_admin_attributes/2_merge_sources/wld.xlsx').resolve()

db = {}
print('Loading Global Admin xlsx...')
sheets = pd.ExcelFile((cwd / lookup_input).resolve())
print('Global Admin xlsx loaded')
for sheet in sheets.sheet_names:
    db[sheet] = sheets.parse(sheet_name=sheet, na_values=na_values,
                             keep_default_na=False)
print('Global Admin xlsx parsed')

wfp_adm0_path = (cwd / '../0_data_inputs/attributes/wfp_adm0.xlsx').resolve()
wfp_adm0 = pd.read_excel(wfp_adm0_path)

print('Loading wld.gpkg...')
gdf_1 = gpd.read_file(input_1, layer='wld')
for level in range(5):
    print(f'wld adm{level}')
    gdf_1 = gdf_1.merge(db[f'adm{level}'], how='left', on=f'id_{level}')
gdf_1 = gdf_1.sort_values(by=list(gdf_1.columns[0:4]))
print('Saving wld.gpkg...')
gdf_1.to_file(output_1, layer='wld', driver="GPKG")

for level in range(5):
    print(f'Loading wld_levels.gpkg, layer=wld_adm{level}...')
    gdf_2 = gpd.read_file(input_2, layer=f'wld_adm{level}')
    for lvl in range(level + 1):
        gdf_2 = gdf_2.merge(db[f'adm{lvl}'], how='left', on=f'id_{lvl}')
    if level == 0:
        gdf_2 = gdf_2.merge(wfp_adm0, how='left', on=['id_0', f'id_wfp_0'])
        gdf_2 = gdf_2.sort_values(by=['id_0', 'id_wfp_0'])
    else:
        gdf_2 = gdf_2.sort_values(by=list(gdf_2.columns[0:level]))
    print(f'Saving wld_levels.gpkg, layer=wld_adm{level}...')
    gdf_2.to_file(output_2, layer=f'wld_adm{level}', driver="GPKG")
