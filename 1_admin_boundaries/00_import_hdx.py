import os
from pathlib import Path
import pandas as pd
from sqlite3 import connect

cwd = Path(__file__).parent
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.db').resolve()
bounds = (cwd / '../0_data_inputs/boundaries/hdx').resolve()


def add_hdx(code: str, level: int):
    columns = [f'id_{x}' for x in range(level+1)]
    in_file = (bounds / f'{code}_adm{level}.gpkg').resolve()
    out_file = (cwd / f'00_inputs/{code}_adm{level}.gpkg')
    tmp_1 = Path(f'{cwd}/00_inputs/{code}_tmp.gpkg')
    tmp_2 = Path(f'{cwd}/00_inputs/{code}_tmp.sqlite')
    layer = f'{code}_adm{level}'
    os.system(
        f"""ogr2ogr \
        -sql "SELECT geom, fid, fid AS fid_0 FROM {layer}" \
        -nln {layer} \
        {tmp_1} {in_file}"""
    )
    conn_1 = connect(in_file)
    df = pd.read_sql_query(f'SELECT * FROM "{layer}"', conn_1)
    conn_1.close()
    for lvl in range(level + 1):
        renamed = {f'id_ocha_{lvl}': f'admin{lvl}Pcode'}
        join = db[f'adm{lvl}'].filter(items=[f'id_{lvl}', f'id_ocha_{lvl}'])
        join = join[join[f'id_{lvl}'].str.contains(code.upper(), na=False)]
        join = join.rename(columns=renamed)
        df = df.merge(join, how='outer', on=f'admin{lvl}Pcode',
                      validate='many_to_one')
    df = df.filter(items=columns)
    df = df.sort_values(by=list(df.columns[:-1]))
    if df.isna().any(axis=None):
        raise ValueError('Dataframe contains NaN values')
    conn_2 = connect(tmp_2)
    df.to_sql(layer, conn_2, if_exists='replace', index=False)
    conn_2.close()
    join_sql = f"""
        SELECT * FROM {layer} AS adm
        INNER JOIN '{tmp_2}'.{layer} AS tbl
        ON adm.fid_0 = tbl.rowid"""
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
        code, level = in_file.name.split('.')[0].split('_adm')
        print(code, level)
        add_hdx(code, int(level))
