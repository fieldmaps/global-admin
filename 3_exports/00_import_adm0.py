import os
import pandas as pd
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.db').resolve()
attrs_adm0 = (cwd / '../0_data_inputs/attributes/wld_adm0.xlsx').resolve()

db_0 = pd.read_excel(attrs_adm0, engine='openpyxl')
conn_0 = connect(attrs)
db_1 = pd.read_sql_query(f'SELECT * FROM adm0', conn_0)
conn_0.close()

points = ((cwd / '../0_data_inputs/boundaries/wld_points.gpkg').resolve(),
          (cwd / '00_import_adm0/wld_points.gpkg').resolve(),
          'points')
polygons = ((cwd / '../0_data_inputs/boundaries/wld_polygons.gpkg').resolve(),
            (cwd / '00_import_adm0/wld_polygons.gpkg').resolve(),
            'polygons')

(cwd / '00_import_adm0').mkdir(parents=True, exist_ok=True)

col_base = {
    'fid': 'fid',
    'geom': 'geom',
}

col_db_0 = {
    'adm0_fid': 'adm0_fid',
    'adm0_id': 'adm0_id',
    'adm0_name': 'adm0_name',
    'adm0_label': 'adm0_label',
    'adm0_cont': 'adm0_cont',
    'adm0_color': 'adm0_color',
    'adm0_stsc': 'adm0_stsc',
    'adm0_stsn': 'adm0_stsn',
}

col_db_1 = {
    'id_ocha_0': 'adm0_ocha',
    'name1_0': 'adm0_name1',
    'name2_0': 'adm0_name2',
    'name3_0': 'adm0_name3',
    'namealt_0': 'adm0_namea',
    'lang1': 'lang_name1',
    'lang2': 'lang_name2',
    'lang3': 'lang_name3',
    'src_name': 'src_name',
    'src_url': 'src_url',
    'src_date': 'src_date',
    'src_valid': 'src_valid',
}

cols = {**col_base, **col_db_0, **col_db_1}

for input, output, layer in [points, polygons]:
    tmp = (cwd / f'00_import_adm0/tmp_{layer}.gpkg').resolve()
    os.system(
        f"""ogr2ogr \
        -sql "SELECT * FROM adm0_{layer} ORDER BY adm0_fid ASC" \
        -unsetFid \
        -dim XY \
        -nln adm0_{layer} \
        {tmp} {input}"""
    )
    conn = connect(tmp)
    df = pd.read_sql_query(f'SELECT * FROM adm0_{layer}', conn)
    df = df.merge(db_0, on='adm0_fid', how='left')
    df = df.merge(db_1, left_on='adm0_id', right_on='id_0', how='left')
    df = df.filter(items=list(cols.keys()))
    df = df.rename(columns=cols)
    df.to_sql(f'adm0_{layer}', conn, if_exists='replace', index=False)
    conn.close()
    os.system(f'ogr2ogr {output} {tmp}')
    os.remove(tmp)
