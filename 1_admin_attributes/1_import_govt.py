import os
from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np

cwd = Path(__file__).parent
Path((cwd / '1_import_govt').resolve()).mkdir(parents=True, exist_ok=True)
input_path = (cwd / '../data.csv').resolve()


def get_col_index():
    res = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5',
           'src_name', 'src_url', 'src_date', 'src_valid', 'lang1', 'lang2', 'lang3']
    for level in range(6):
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


def split_df(df, row, level):
    col_index = get_col_index()
    output = {}
    join = pd.DataFrame()
    df = add_standard_ids(df, row, level)
    for lvl in range(level + 1):
        df2 = df.copy()
        df2 = df2.filter(regex=f'^.+_{lvl}$')
        if lvl == 0:
            df2['src_name'] = row['source']
            df2['src_url'] = row['url']
            df2['src_date'] = date.fromisoformat(row['date'])
            df2['src_valid'] = date.fromisoformat(row['valid_on'])
            df2['id_ocha_0'] = row['alpha_2']
            for lang in ['lang1', 'lang2', 'lang3']:
                if str(row[lang]) != 'nan':
                    df2[lang] = row[lang]
        cols = list(filter(lambda x: x in df2.columns, col_index))
        df2 = df2.reindex(cols, axis=1)
        output[f'adm{lvl}'] = df2.drop_duplicates()
        join[f'id_{lvl}'] = df2[f'id_{lvl}']
    return {'join': join, **output}


def add_standard_ids(df, country, level):
    for lvl in range(level + 1):
        df = df.sort_values(f'id_govt_{lvl}')
        if lvl == 0:
            df['id_0'] = country['alpha_3']
            df['id_ocha_0'] = country['alpha_2']
        else:
            df[f'id_ocha_{lvl}'] = country['alpha_2'] + df[f'id_govt_{lvl}']
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


for index, row in pd.read_csv(input_path).iterrows():
    code = row['alpha_3'].lower()
    level = int(row['admin_level_full'])
    if row['url'] is np.nan or row['url'].startswith('https://data.humdata.org'):
        continue
    print(code)
    hdx_file = f'../0_data_inputs/attributes/govt/{code}.xlsx'
    df = pd.read_excel((cwd / hdx_file).resolve(),
                       converters={'id_govt_0': str, 'id_govt_1': str,
                                   'id_govt_2': str, 'id_govt_3': str,
                                   'id_govt_4': str, 'id_govt_5': str})
    db = split_df(df, row, level)
    output = (cwd / f'1_import_govt/{code}.xlsx').resolve()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for key, value in db.items():
        value.to_excel(writer, sheet_name=key, startrow=1,
                       header=False, index=False)
        worksheet = writer.sheets[key]
        for idx, val in enumerate(value.columns):
            worksheet.write(0, idx, val)
    writer.save()
