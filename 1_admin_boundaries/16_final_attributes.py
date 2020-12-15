import os
import csv
from pathlib import Path
import pandas as pd
import numpy as np
from sqlite3 import connect

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()


def final_attributes(code, level):
    input = Path(f'{cwd}/15_final_union/{code}.gpkg')
    tmp_1 = Path(f'{cwd}/16_final_attributes/{code}_tmp.gpkg')
    tmp_2 = Path(f'{cwd}/16_final_attributes/{code}_tmp.sqlite')
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


with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        final_attributes(code, level)
