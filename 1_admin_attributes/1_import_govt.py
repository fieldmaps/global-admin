import csv
from pathlib import Path
import pandas as pd
import numpy as np
import shutil
from sqlite3 import connect

cwd = Path(__file__).parent
input_path = (cwd / '../0_data_inputs/attributes/govt').resolve()
output_path = (cwd / '1_import_govt').resolve()
shutil.rmtree(output_path, ignore_errors=True)
output_path.mkdir(parents=True, exist_ok=True)


def get_col_index():
    res = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4',
           'src_name', 'src_url', 'src_date', 'src_valid', 'lang1', 'lang2', 'lang3']
    for level in range(5):
        column_names = ['name1', 'name2', 'name3', 'namealt',
                        'type1', 'type2', 'type3', 'typealt',
                        'id_ocha', 'id_wfp', 'id_gadm', 'id_govt']
        res.extend([s + f'_{level}' for s in column_names])
    return res


def col_str(df, col):
    if col in df.columns:
        df[col] = df[col].fillna('')
        df[col] = df[col].apply(str)
    return df


def split_df(df, iso3, iso2, level):
    col_index = get_col_index()
    output = {}
    join = pd.DataFrame()
    df = add_standard_ids(df, iso3, iso2, level)
    for lvl in range(level + 1):
        df2 = df.copy()
        df2 = df2.filter(regex=f'^.+_{lvl}$')
        if lvl == 0:
            df2['src_name'] = 'GOVT'
            df2['src_url'] = np.nan
            df2['src_date'] = np.nan
            df2['src_valid'] = np.nan
            df2['id_ocha_0'] = iso2
            df2['lang1'] = 'en'
            if iso3 == 'CAN':
                df2['lang2'] = 'fr'
        cols = list(filter(lambda x: x in df2.columns, col_index))
        df2 = df2.reindex(cols, axis=1)
        output[f'adm{lvl}'] = df2.drop_duplicates()
        join[f'id_{lvl}'] = df2[f'id_{lvl}']
    return {'join': join, **output}


def add_standard_ids(df, iso3, iso2, level):
    for lvl in range(level + 1):
        df = df.sort_values(f'id_govt_{lvl}')
        if lvl == 0:
            df['id_0'] = iso3
            df['id_ocha_0'] = iso2
        else:
            df[f'id_ocha_{lvl}'] = iso2 + df[f'id_govt_{lvl}']
            col = f'id_govt_{lvl}'
            col_higher = f'id_{lvl-1}'
            prev_id = None
            higher_id = None
            id_num = None
            for index, row in df.iterrows():
                if row[col_higher] != higher_id:
                    id_num = 1
                elif row[col] != prev_id:
                    id_num = id_num + 1
                higher_id = row[col_higher]
                prev_id = row[col]
                new_val = f'{higher_id}{id_num:03}'
                if id_num > 999:
                    raise ValueError('Value above 999 not supported')
                if not pd.isna(row[col]):
                    df.at[index, f'id_{lvl}'] = new_val
    return df


iso2_lookup = {}
with open((cwd / '../country-codes.csv').resolve(), mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        iso2_lookup[row['alpha-3']] = row['alpha-2']

files_in_path = sorted(input_path.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.xlsx':
        code, level = in_file.name.split('.')[0].split('_adm')
        level = int(level)
        print(code, level)
        df = pd.read_excel(in_file, engine='openpyxl', converters={
            'id_govt_0': str, 'id_govt_1': str, 'id_govt_2': str,
            'id_govt_3': str, 'id_govt_4': str})
        db = split_df(df, code.upper(), iso2_lookup[code.upper()], level)
        output = (output_path / f'{code}.db').resolve()
        conn = connect(output)
        for table in db:
            db[table].to_sql(table, conn, index=False)
        conn.close()
