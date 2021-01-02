import os
import re
from pathlib import Path
import pandas as pd
import numpy as np
from sqlite3 import connect

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()
bounds = (cwd / '15_final_union').resolve()


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


def final_attributes(code, level):
    input = Path(f'{cwd}/15_final_union/{code}.gpkg')
    tmp_1 = Path(f'{cwd}/16_final_attributes/{code}_tmp.gpkg')
    tmp_2 = Path(f'{cwd}/16_final_attributes/{code}_tmp.db')
    output = Path(f'{cwd}/16_final_attributes/{code}.gpkg')
    layer = f'{code}_adm{level}'
    if os.path.isfile(input):
        os.system(
            f"""ogr2ogr \
            -sql "SELECT geom, fid, fid AS fid_0 FROM {layer}" \
            -nln {layer} \
            {tmp_1} {input}"""
        )
        conn_1 = connect(input)
        df = pd.read_sql_query(f'SELECT * FROM "{layer}"', conn_1)
        conn_1.close()
        df = df.drop('geom', 1)
        df = df.drop('fid_2', 1)
        df = df.drop('id_0_2_2', 1)
        for l in range(level+1):
            attribute = f'id_{l}'
            df[attribute] = np.where(df[attribute].isna(),
                                     df[attribute + '_2'],
                                     df[attribute])
            df = df.drop(attribute + '_2', 1)
        columns = ','.join(df.columns[1:])
        conn_2 = connect(tmp_2)
        df.to_sql(layer, conn_2, if_exists='replace', index=False)
        conn_2.close()
        join_sql = f"""
            SELECT * FROM {layer} AS adm
            INNER JOIN '{tmp_2}'.{layer} AS tbl
            ON adm.fid_0 = tbl.fid"""
        os.system(
            f"""ogr2ogr \
            -dialect INDIRECT_SQLITE \
            -sql "{join_sql}" \
            -select '{columns}' \
            -nln {layer} \
            {output} {tmp_1}"""
        )
        os.remove(tmp_1)
        os.remove(tmp_2)


files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        print(code, level)
        final_attributes(code, level)
