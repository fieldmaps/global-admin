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
db_1['wfp_update'] = db_1['wfp_update'].dt.date

points = ((cwd / '../0_data_inputs/boundaries/wld_points.gpkg').resolve(),
          (cwd / '00_import_adm0/wld_points.gpkg').resolve(),
          'points')
polygons = ((cwd / '../0_data_inputs/boundaries/wld_polygons.gpkg').resolve(),
            (cwd / '00_import_adm0/wld_polygons.gpkg').resolve(),
            'polygons')

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
    'id_wfp_0': 'wfp_id',
}

cols = {**col_base, **col_lvl(0), **col_adm0}

for input, output, layer in [polygons, points]:
    tmp = (cwd / f'00_import_adm0/tmp_{layer}.gpkg').resolve()
    os.system(
        f"""ogr2ogr \
        -sql "SELECT * FROM adm0 ORDER BY id_0, id_wfp_0 ASC" \
        -unsetFid \
        -nln adm0 \
        {tmp} {input}"""
    )
    conn = connect(tmp)
    df = pd.read_sql_query(f'SELECT * FROM adm0', conn)
    df = df.merge(db_0, on='id_0', how='left')
    df = df.filter(items=list(cols.keys()))
    df = df.rename(columns=cols)
    df = df.merge(db_1, on=['adm0_id', 'wfp_id'], how='left')
    df.to_sql('adm0', conn, if_exists='replace', index=False)
    conn.close()
    os.system(f'ogr2ogr {output} {tmp}')
    os.remove(tmp)
