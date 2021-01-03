import os
import pandas as pd
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.db').resolve()
attrs_adm0 = (cwd / '../0_data_inputs/attributes/wld_adm0.xlsx').resolve()

conn_0 = connect(attrs)
db_0 = pd.read_sql_query(f'SELECT * FROM adm0', conn_0)
conn_0.close()
db_1 = pd.read_excel(attrs_adm0, engine='openpyxl')
db_1['lst_update'] = db_1['lst_update'].dt.date

polygons = ((cwd / '../0_data_inputs/boundaries/wld_polygons.gpkg').resolve(),
            (cwd / '00_import_adm0/wld_polygons.gpkg').resolve())
points = ((cwd / '../0_data_inputs/boundaries/wld_points.gpkg').resolve(),
          (cwd / '00_import_adm0/wld_points.gpkg').resolve())
tmp = (cwd / f'00_import_adm0/tmp.gpkg').resolve()

(cwd / '00_import_adm0').mkdir(parents=True, exist_ok=True)


def col_lvl(level):
    result = {}
    for l in range(level+1, -1, -1):
        result.update({
            f'id_{l}': f'adm{l}_id',
            f'id_ocha_{l}': f'adm{l}_ocha',
            f'name1_{l}': f'adm{l}_name1',
            f'name2_{l}': f'adm{l}_name2',
            f'name3_{l}': f'adm{l}_name3',
            f'namealt_{l}': f'adm{l}_namea',
        })
    return result


col_base = {
    'fid': 'fid',
    'geom': 'geom',
}

col_adm0 = {
    'lang1': 'lang_name1',
    'lang2': 'lang_name2',
    'lang3': 'lang_name3',
    'src_name': 'src_name',
    'src_url': 'src_url',
    'src_date': 'src_date',
    'src_valid': 'src_valid',
}

col_adm0_wfp = {
    'id_wfp_0': 'wfp_id',
    'name_wfp': 'wfp_name',
    'name_wfp1': 'wfp_namea',
    'disp_area': 'wfp_disput',
    'source': 'wfp_source',
    'stscod': 'wfp_status',
    'map_lab': 'wfp_label',
    'mapclr': 'wfp_mapclr',
    'lst_update': 'wfp_update',
}

cols = {**col_base, **col_lvl(0), **col_adm0, **col_adm0_wfp}

for input, output in [polygons, points]:
    os.system(
        f"""ogr2ogr \
        -sql "SELECT * FROM adm0" \
        -nln adm0 \
        {tmp} {input}"""
    )
    conn = connect(tmp)
    df = pd.read_sql_query(f'SELECT * FROM adm0', conn)
    df = df.merge(db_0, on='id_0', how='left')
    df = df.merge(db_1, on=['id_0', 'id_wfp_0'], how='left')
    df = df.filter(items=list(cols.keys()))
    df = df.rename(columns=cols)
    df.to_sql('adm0', conn, if_exists='replace', index=False)
    conn.close()
    os.system(
        f"""ogr2ogr \
        -sql "SELECT * FROM adm0 ORDER BY adm0_id ASC" \
        -unsetFid \
        -nln adm0 \
        {output} {tmp}"""
    )
    os.remove(tmp)
