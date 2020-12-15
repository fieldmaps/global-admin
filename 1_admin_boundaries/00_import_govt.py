import os
import csv
from pathlib import Path
import pandas as pd
from sqlite3 import connect

cwd = Path(__file__).parent
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.sqlite').resolve()


def get_converters():
    res = {}
    items = ['name1', 'name2', 'name3', 'namealt',
             'type1', 'typealt', 'id_govt', 'id_ocha']
    for lvl in range(6):
        for item in items:
            res[f'{item}_{lvl}'] = str
    return res


def add_govt(code, level):
    columns = [f'id_{x}' for x in range(level+1)]
    input = (cwd / f'../0_data_inputs/boundaries/govt/{code}.gpkg').resolve()
    output = (cwd / f'00_inputs/{code}.gpkg').resolve()
    tmp_1 = Path(f'{cwd}/00_inputs/{code}_tmp.gpkg')
    tmp_2 = Path(f'{cwd}/00_inputs/{code}_tmp.sqlite')
    layer = f'{code}_adm{level}'
    os.system(
        f"""ogr2ogr \
        -sql "SELECT geom, fid, fid AS fid_0 FROM {layer}" \
        -nln {layer} \
        {tmp_1} {input}"""
    )
    conn_1 = connect(input)
    df = pd.read_sql_query(f'SELECT * FROM "{layer}"', conn_1)
    conn_1.close()
    for lvl in range(level + 1):
        join = db[f'adm{lvl}'].filter(items=[f'id_{lvl}', f'id_govt_{lvl}'])
        join = join[join[f'id_{lvl}'].str.contains(code.upper(), na=False)]
        df = df.merge(join, how='outer', on=f'id_govt_{lvl}',
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
        {output} {tmp_1}"""
    )
    os.remove(tmp_1)
    os.remove(tmp_2)


db = {}
conn = connect(attrs)
for level in range(5):
    db[f'adm{level}'] = pd.read_sql(f'SELECT * from adm{level}', conn)

with open((cwd / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        if row['url'] == '' or row['url'].startswith('https://data.humdata.org'):
            continue
        print(code)
        add_govt(code, level)
