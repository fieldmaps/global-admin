import pandas as pd
import numpy as np
from sqlite3 import connect
import shutil
from pathlib import Path


def tables_in_sqlite_db(conn):
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    return tables


def col_str(df, col):
    if col in df.columns:
        df[col] = df[col].fillna('')
        df[col] = df[col].apply(str)
    return df


def col_na(df, col):
    if col in df.columns:
        df[col] = df[col].replace('', np.nan)
    return df


def get_col_index():
    res = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4',
           'src_name', 'src_url', 'src_date', 'src_valid', 'lang1', 'lang2', 'lang3']
    for level in range(5):
        column_names = ['name1', 'name2', 'name3', 'namealt',
                        'type1', 'type2', 'type3', 'typealt', 'id_ocha', 'id_gadm', 'id_govt']
        res.extend([s + f'_{level}' for s in column_names])
    return res


col_index = get_col_index()
output = {}

cwd = Path(__file__).parent
gadm_path = (cwd / '1_import_gadm').resolve()
govt_path = (cwd / '1_import_govt').resolve()
hdx_path = (cwd / '1_import_hdx').resolve()

tmp_path = (cwd / '2_merge_sources_tmp').resolve()
output_path = (cwd / '2_merge_sources').resolve()

shutil.rmtree(tmp_path, ignore_errors=True)
shutil.copytree(gadm_path, tmp_path, dirs_exist_ok=True)
shutil.copytree(govt_path, tmp_path, dirs_exist_ok=True)
shutil.copytree(hdx_path, tmp_path, dirs_exist_ok=True)

for path in sorted(tmp_path.glob('*.db')):
    print(path.name)
    conn = connect(path)
    tables = tables_in_sqlite_db(conn)
    for table in tables:
        df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
        if table != 'join':
            level = int(table[-1])
            df = col_str(df, f'name1_{level}')
            df = col_str(df, f'name2_{level}')
            df = col_str(df, f'name3_{level}')
            df = col_str(df, f'namealt_{level}')
            df = col_str(df, f'type1_{level}')
            df = col_str(df, f'typealt_{level}')
            df = col_str(df, f'id_govt_{level}')
            df = col_str(df, f'id_ocha_{level}')
        if table in output:
            output[table] = output[table].merge(df, how='outer')
        else:
            output[table] = df
    conn.close()

shutil.rmtree(tmp_path)
shutil.rmtree(output_path, ignore_errors=True)
output_path.mkdir(parents=True, exist_ok=True)
conn = connect((output_path / 'wld.db').resolve())

for table, df in output.items():
    print(table)
    if table != 'join':
        level = int(table[-1])
        df = col_na(df, f'name1_{level}')
        df = col_na(df, f'name2_{level}')
        df = col_na(df, f'name3_{level}')
        df = col_na(df, f'namealt_{level}')
        df = col_na(df, f'type1_{level}')
        df = col_na(df, f'typealt_{level}')
        df = col_na(df, f'id_govt_{level}')
        df = col_na(df, f'id_ocha_{level}')
        if not df[f'id_{level}'].is_unique:
            raise ValueError(f'Duplicate ID value in {table}')
    cols = list(filter(lambda x: x in df.columns, col_index))
    df = df.reindex(cols, axis=1)
    df = df.sort_values(by=cols)
    df.to_sql(table, conn, index=False)

conn.close()
