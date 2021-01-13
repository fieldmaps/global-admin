import os
import re
import pandas as pd
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.db').resolve()
bounds = (cwd / '../2_admin_boundaries/21_final_higher_attrs').resolve()

(cwd / '00_import_boundless').mkdir(parents=True, exist_ok=True)

db = {}
conn_0 = connect(attrs)
for level in range(5):
    db[f'adm{level}'] = pd.read_sql_query(f'SELECT * FROM adm{level}', conn_0)
conn_0.close()


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


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


def add_boundless(input, code: str, level: int):
    tmp = (cwd / f'00_import_boundless/{code}_tmp.gpkg').resolve()
    output = (cwd / f'00_import_boundless/{code}.gpkg').resolve()
    for level in range(level+1):
        print(f'{code} {level}')
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM {code}_adm{level} ORDER BY id_{level} ASC" \
            -unsetFid \
            -nln {code}_adm{level} \
            {'-append' if level > 0 else ''} \
            {tmp} {input}"""
        )
        conn = connect(tmp)
        df = pd.read_sql_query(f'SELECT * FROM "{code}_adm{level}"', conn)
        for lvl in range(level, -1, -1):
            df = df.merge(db[f'adm{lvl}'], on=f'id_{lvl}')
        cols = {**col_base, **col_lvl(level), **col_adm0}
        df = df.filter(items=list(cols.keys()))
        df = df.rename(columns=cols)
        df.to_sql(f'{code}_adm{level}', conn, if_exists='replace', index=False)
        conn.close()
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM {code}_adm{level} ORDER BY adm{level}_id ASC" \
            -unsetFid \
            -nln {code}_adm{level} \
            {'-append' if level > 0 else ''} \
            {output} {tmp}"""
        )
        os.remove(tmp)


files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        if level > 0:
            add_boundless(in_file, code, level)
