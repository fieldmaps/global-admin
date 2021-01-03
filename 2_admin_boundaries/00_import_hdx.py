import os
import re
from pathlib import Path
import pandas as pd
from sqlite3 import connect

cwd = Path(__file__).parent
(cwd / f'00_inputs').mkdir(parents=True, exist_ok=True)
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.db').resolve()
bounds = (cwd / '../0_data_inputs/boundaries/hdx').resolve()


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


def add_hdx(code: str, level: int):
    columns = [f'id_{x}' for x in range(level+1)]
    in_file = (bounds / f'{code}.gpkg').resolve()
    out_file = (cwd / f'00_inputs/{code}.gpkg')
    tmp_1 = Path(f'{cwd}/00_inputs/{code}_tmp.gpkg')
    tmp_2 = Path(f'{cwd}/00_inputs/{code}_tmp.db')
    layer = f'{code}_adm{level}'
    os.system(
        f"""ogr2ogr \
        -sql "SELECT fid,geom,admin{level}Pcode FROM {layer}" \
        -nln {layer} \
        {tmp_1} {in_file}"""
    )
    conn_1 = connect(in_file)
    df = pd.read_sql_query(f'SELECT * FROM "{layer}"', conn_1)
    conn_1.close()
    for lvl in range(level + 1):
        join = db[f'adm{lvl}'].filter(items=[f'id_{lvl}', f'id_ocha_{lvl}'])
        join = join[join[f'id_{lvl}'].str.contains(code.upper(), na=False)]
        join = join.rename(columns={f'id_ocha_{lvl}': f'admin{lvl}Pcode'})
        df = df.merge(join, how='left', on=f'admin{lvl}Pcode',
                      validate='many_to_one')
    if df.isna().any(axis=None):
        raise ValueError('Dataframe contains NaN values')
    conn_2 = connect(tmp_2)
    df.to_sql(layer, conn_2, if_exists='replace', index=False)
    conn_2.close()
    join_sql = f"""
        SELECT * FROM {layer} AS adm
        LEFT JOIN '{tmp_2}'.{layer} AS tbl
        ON adm.admin{level}Pcode = tbl.admin{level}Pcode"""
    os.system(
        f"""ogr2ogr \
        -dialect INDIRECT_SQLITE \
        -sql "{join_sql}" \
        -select '{','.join(columns)}' \
        -nln {layer} \
        {out_file} {tmp_1}"""
    )
    os.remove(tmp_1)
    os.remove(tmp_2)


db = {}
conn = connect(attrs)
for level in range(5):
    db[f'adm{level}'] = pd.read_sql_query(f'SELECT * FROM adm{level}', conn)
conn.close()

files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        print(code, level)
        add_hdx(code, int(level))
