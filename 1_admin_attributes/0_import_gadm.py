from datetime import date
from pathlib import Path
import pandas as pd
import numpy as np


def add_gadm(code, code2):
    output = (cwd / f'0_import_gadm/{code.lower()}.xlsx').resolve()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df_country = df[df.id_0.str.contains(code, na=False)]
    df_split = get_columns(df_country, code2)
    for key, value in df_split.items():
        value.to_excel(writer, sheet_name=key, startrow=1,
                       header=False, index=False)
        worksheet = writer.sheets[key]
        for idx, val in enumerate(value.columns):
            worksheet.write(0, idx, val)
    writer.save()


def get_columns(df, code2):
    if not df.id_5.isnull().all():
        return split_df(df, code2, ['0', '1', '2', '3', '4', '5'])
    if not df.id_4.isnull().all():
        return split_df(df, code2, ['0', '1', '2', '3', '4'])
    if not df.id_3.isnull().all():
        return split_df(df, code2, ['0', '1', '2', '3'])
    if not df.id_2.isnull().all():
        return split_df(df, code2, ['0', '1', '2'])
    if not df.id_1.isnull().all():
        return split_df(df, code2, ['0', '1'])
    return split_df(df, code2, ['0'])


def split_df(df, code2, levels):
    col_index = ['id', 'name_1', 'name_alt', 'lang_1', 'type_1', 'type_alt',
                 'src_name', 'src_url', 'src_date', 'src_valid',
                 'code_gadm', 'code_govt', 'code_ocha']
    output = {}
    join = pd.DataFrame()
    for level in levels:
        df_level = df.filter(regex=f'^.+_{level}$')
        df_level.columns = df_level.columns.str.replace(f'_{level}$', '')
        df_level = df_level.assign(code_gadm=df_level['id'])
        if level == '0':
            df_level['lang_1'] = 'en'
            df_level['src_name'] = 'GADM'
            df_level['src_url'] = 'https://gadm.org'
            df_level['src_date'] = None
            df_level['src_valid'] = date(2018, 5, 6)
            df_level['code_ocha'] = code2
        df_level = reformat_id(df_level, code2)
        cols = list(filter(lambda x: x in df_level.columns, col_index))
        df_level = df_level.reindex(cols, axis=1)
        output[f'adm{level}'] = df_level.drop_duplicates()
        join[f'id_{level}'] = df_level['id']
    return {'join': join, **output}


def reformat_id(df, code2):
    for index, row in df.iterrows():
        split_id = row['id'].split('_')[0].split('.')
        new_id = split_id.pop(0)
        new_ocha = code2
        for id in split_id:
            if int(id) > 999:
                raise ValueError('Value above 999 not supported')
            new_id = f'{new_id}{int(id):03}'
            new_ocha = f'{new_ocha}{int(id):03}'
        df.at[index, 'id'] = new_id
        df.at[index, 'code_ocha'] = new_ocha
    return df


col_0 = {
    'GID_0': 'id_0',
    'NAME_0': 'name_1_0',
}
col_1 = {
    'GID_1': 'id_1',
    'NAME_1': 'name_1_1',
    'NAME_ALT_1': 'name_alt_1',
    'ENGTYPE_1': 'type_1_1',
    'TYPE_1': 'type_alt_1',
    'CC_1': 'code_govt_1',
}
col_2 = {
    'GID_2': 'id_2',
    'NAME_2': 'name_1_2',
    'NAME_ALT_2': 'name_alt_2',
    'ENGTYPE_2': 'type_1_2',
    'TYPE_2': 'type_alt_2',
    'CC_2': 'code_govt_2',
}
col_3 = {
    'GID_3': 'id_3',
    'NAME_3': 'name_1_3',
    'NAME_ALT_3': 'name_alt_3',
    'ENGTYPE_3': 'type_1_3',
    'TYPE_3': 'type_alt_3',
    'CC_3': 'code_govt_3',
}
col_4 = {
    'GID_4': 'id_4',
    'NAME_4': 'name_1_4',
    'NAME_ALT_4': 'name_alt_4',
    'ENGTYPE_4': 'type_1_4',
    'TYPE_4': 'type_alt_4',
    'CC_4': 'code_govt_4',
}
col_5 = {
    'GID_5': 'id_5',
    'NAME_5': 'name_1_5',
    'NAME_ALT_5': 'name_alt_5',
    'ENGTYPE_5': 'type_1_5',
    'TYPE_5': 'type_alt_5',
    'CC_5': 'code_govt_5',
}

col_new = {**col_0, **col_1, **col_2, **col_3, **col_4, **col_5}
re_filter = r'^[Ww]ater\s?[Bb]ody|Lake$'
cwd = Path(__file__).parent

Path((cwd / '0_import_gadm').resolve()).mkdir(parents=True, exist_ok=True)
input_1 = (cwd / '../0_data_inputs/attributes/gadm36.xlsx').resolve()
print('Loading GADM xlsx...')
df = pd.read_excel(input_1)
print('GADM xlsx loaded')

df = df[~df.ENGTYPE_1.str.contains(re_filter, na=False)]
df = df[~df.ENGTYPE_2.str.contains(re_filter, na=False)]
df = df[~df.ENGTYPE_3.str.contains(re_filter, na=False)]
df = df[~df.ENGTYPE_4.str.contains(re_filter, na=False)]
df = df[~df.ENGTYPE_5.str.contains(re_filter, na=False)]

df['NAME_ALT_1'] = df.VARNAME_1.apply(str).str.cat(df.NL_NAME_1.apply(
    str), sep='|').replace('nan|nan', np.nan).replace(r'^nan\||\|nan$', '', regex=True)
df['NAME_ALT_2'] = df.VARNAME_2.apply(str).str.cat(df.NL_NAME_2.apply(
    str), sep='|').replace('nan|nan', np.nan).replace(r'^nan\||\|nan$', '', regex=True)
df['NAME_ALT_3'] = df.VARNAME_3.apply(str).str.cat(df.NL_NAME_3.apply(
    str), sep='|').replace('nan|nan', np.nan).replace(r'^nan\||\|nan$', '', regex=True)
df['NAME_ALT_4'] = df.VARNAME_4.apply(str).replace('nan', np.nan)
df['NAME_ALT_5'] = None

df = df.filter(items=list(col_new.keys()))
df = df.rename(columns=col_new)

countries = pd.read_excel((cwd / '../data.xlsx').resolve())
for index, country in countries.iterrows():
    print(country['alpha_3'])
    add_gadm(country['alpha_3'], country['alpha_2'])
