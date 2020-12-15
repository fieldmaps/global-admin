from datetime import date
from pathlib import Path
import csv
import pandas as pd
import numpy as np
import shutil
from sqlite3 import connect


def add_gadm(code, code2):
    output = (cwd / f'1_import_gadm/{code.lower()}.db').resolve()
    df_country = df[df['id_gadm_0'].str.contains(code, na=False)]
    df_split = get_columns(df_country, code2)
    conn = connect(output)
    for table in df_split:
        df_split[table].to_sql(table, conn, index=False)
    conn.close()


def get_columns(df, code2):
    if not df['id_gadm_4'].isna().all():
        return split_df(df, code2, ['0', '1', '2', '3', '4'])
    if not df['id_gadm_3'].isna().all():
        return split_df(df, code2, ['0', '1', '2', '3'])
    if not df['id_gadm_2'].isna().all():
        return split_df(df, code2, ['0', '1', '2'])
    if not df['id_gadm_1'].isna().all():
        return split_df(df, code2, ['0', '1'])
    return split_df(df, code2, ['0'])


def get_col_index():
    res = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4',
           'src_name', 'src_url', 'src_date', 'src_valid', 'lang1', 'lang2', 'lang3']
    for level in range(5):
        column_names = ['name1', 'name2', 'name3', 'namealt',
                        'type1', 'type2', 'type3', 'typealt',
                        'id_ocha', 'id_wfp', 'id_gadm', 'id_govt']
        res.extend([s + f'_{level}' for s in column_names])
    return res


def split_df(df, code2, levels):
    col_index = get_col_index()
    output = {}
    join = pd.DataFrame()
    for level in levels:
        df_level = df.copy()
        df_level = df_level.filter(regex=f'^.+_{level}$')
        if level == '0':
            df_level['lang1'] = 'en'
            df_level['src_name'] = 'GADM'
            df_level['src_url'] = 'https://gadm.org'
            df_level['src_date'] = None
            df_level['src_valid'] = date(2018, 5, 6)
            df_level['id_ocha_0'] = code2
        df_level = reformat_id(df_level, code2, level)
        cols = list(filter(lambda x: x in df_level.columns, col_index))
        df_level = df_level.reindex(cols, axis=1)
        output[f'adm{level}'] = df_level.drop_duplicates()
        join[f'id_{level}'] = df_level[f'id_{level}']
    return {'join': join, **output}


def reformat_id(df, code2, level):
    for index, row in df.iterrows():
        split_id = row[f'id_gadm_{level}'].split('_')[0].split('.')
        new_id = split_id.pop(0)
        new_ocha = code2
        for id in split_id:
            if int(id) > 999:
                raise ValueError('Value above 999 not supported')
            new_id = f'{new_id}{int(id):03}'
            new_ocha = f'{new_ocha}{int(id):03}'
        df.at[index, f'id_{level}'] = new_id
        df.at[index, f'id_ocha_{level}'] = new_ocha
    return df


col_0 = {
    'GID_0': 'id_gadm_0',
    'NAME_0': 'name1_0',
}
col_1 = {
    'GID_1': 'id_gadm_1',
    'NAME_1': 'name1_1',
    'NAME_ALT_1': 'namealt_1',
    'ENGTYPE_1': 'type1_1',
    'TYPE_1': 'typealt_1',
    'CC_1': 'id_govt_1',
}
col_2 = {
    'GID_2': 'id_gadm_2',
    'NAME_2': 'name1_2',
    'NAME_ALT_2': 'namealt_2',
    'ENGTYPE_2': 'type1_2',
    'TYPE_2': 'typealt_2',
    'CC_2': 'id_govt_2',
}
col_3 = {
    'GID_3': 'id_gadm_3',
    'NAME_3': 'name1_3',
    'NAME_ALT_3': 'namealt_3',
    'ENGTYPE_3': 'type1_3',
    'TYPE_3': 'typealt_3',
    'CC_3': 'id_govt_3',
}
col_4 = {
    'GID_4': 'id_gadm_4',
    'NAME_4': 'name1_4',
    'NAME_ALT_4': 'namealt_4',
    'ENGTYPE_4': 'type1_4',
    'TYPE_4': 'typealt_4',
    'CC_4': 'id_govt_4',
}

col_new = {**col_0, **col_1, **col_2, **col_3, **col_4}
re_filter = r'^[Ww]ater\s?[Bb]ody|Lake$'
cwd = Path(__file__).parent

output_path = (cwd / '1_import_gadm').resolve()
shutil.rmtree(output_path, ignore_errors=True)
output_path.mkdir(parents=True, exist_ok=True)

input_1 = (cwd / '../0_data_inputs/boundaries/gadm36.gpkg').resolve()
print('Loading GADM DB...')
conn_1 = connect(input_1)
df = pd.read_sql_query('SELECT * FROM gadm', conn_1)
conn_1.close()
print('GADM DB loaded')

df = df[~df['ENGTYPE_1'].str.contains(re_filter, na=False)]
df = df[~df['ENGTYPE_2'].str.contains(re_filter, na=False)]
df = df[~df['ENGTYPE_3'].str.contains(re_filter, na=False)]
df = df[~df['ENGTYPE_4'].str.contains(re_filter, na=False)]

df['NAME_ALT_1'] = df['VARNAME_1'].apply(str).str.cat(df['NL_NAME_1'].apply(
    str), sep='|').replace('None|None', np.nan).replace(r'^None\||\|None$', '', regex=True)
df['NAME_ALT_2'] = df['VARNAME_2'].apply(str).str.cat(df['NL_NAME_2'].apply(
    str), sep='|').replace('None|None', np.nan).replace(r'^None\||\|None$', '', regex=True)
df['NAME_ALT_3'] = df['VARNAME_3'].apply(str).str.cat(df['NL_NAME_3'].apply(
    str), sep='|').replace('None|None', np.nan).replace(r'^None\||\|None$', '', regex=True)
df['NAME_ALT_4'] = df['VARNAME_4'].apply(str).replace('None', np.nan)

df = df.filter(items=list(col_new.keys()))
df = df.rename(columns=col_new)

iso2_lookup = {}
with open((cwd / '../country-codes.csv').resolve(), mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        iso2_lookup[row['alpha-3']] = row['alpha-2']

for iso3 in df['id_gadm_0'].unique():
    if not iso3.startswith('X'):
        print(iso3)
        add_gadm(iso3, iso2_lookup[iso3])
