import os
from pathlib import Path
import pandas as pd
import numpy as np


def parse_sheet(sheets, sheet):
    level = int(sheet[-1])
    na_values = ['', '#N/A']
    df = sheets.parse(sheet_name=sheet, na_values=na_values,
                      keep_default_na=False)
    df = df.replace(regex=r'^\s+$', value=np.nan)
    df = df.replace(regex=[r'^\s+', r'\s+$'], value='')
    df = df.dropna(how='all')
    df = df.drop_duplicates()
    return df, level


def rename_lang(df, level):
    col_name = list(df.filter(regex=r'^admin\dName_'))
    langs = list(map(lambda x: x.split('_')[1], col_name))
    for i, name in enumerate(col_name):
        kwargs = {f'name{i+1}_{level}': df[name]}
        df = df.assign(**kwargs)
    df = make_name_alt(df, level)
    if level == 0:
        for i, lang in enumerate(langs):
            df[f'lang{i+1}'] = lang
    df = df.drop(col_name, axis=1)
    return df


def make_name_alt(df, level):
    def join(row): return '|'.join(row.fillna(''))
    col_name_alt = list(df.filter(regex=r'^admin\dAltName'))
    df[f'namealt_{level}'] = df[col_name_alt].apply(join, axis=1)
    df = df.replace(regex=[r'\|*$', r'^\|*'], value='')
    df = df.drop(col_name_alt, axis=1)
    return df


def adm0_processing(df, db, row):
    new_date = {'date': 'src_date', 'validOn': 'src_valid'}
    re_adm0 = r'^admin0Pcode|^admin0Name_|^admin0AltName_|^date$|^validOn$'
    df = df.filter(regex=re_adm0)
    df = rename_lang(df, 0)
    df['src_name'] = row['source']
    df['src_url'] = row['url']
    df = df.rename(columns=new_date)
    df['src_date'] = df['src_date'].dt.date
    df['src_valid'] = df['src_valid'].dt.date
    db['join']['admin0Pcode'] = df['admin0Pcode']
    return df


def admn_processing(df, db, level):
    pcodes = list(df.filter(regex=r'^admin\dPcode$'))
    sub = df.filter(items=pcodes)
    pcodes.pop(0)
    db['join'] = db['join'].merge(sub, on=pcodes, how='outer')
    db['join'] = db['join'].drop_duplicates()
    db['join'] = db['join'].sort_values(list(db['join'].columns))
    re = '^admin{0}Pcode|^admin{0}Name_|^admin{0}AltName'.format(level)
    df = df.filter(regex=re)
    df = df.drop_duplicates()
    df = df.sort_values(f'admin{level}Pcode')
    df = rename_lang(df, level)
    return df


def clean_join(df, country):
    for col in df.columns:
        if col == 'admin0Pcode':
            df['id_0'] = country['alpha_3']
        else:
            level = int(col[5])
            col_higher = f'id_{level-1}'
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
                    df.at[index, f'id_{level}'] = new_val
    return df


def get_col_index():
    res = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5',
           'src_name', 'src_url', 'src_date', 'src_valid', 'lang1', 'lang2', 'lang3']
    for level in range(6):
        column_names = ['name1', 'name2', 'name3', 'namealt',
                        'type1', 'type2', 'type3', 'typealt',
                        'id_ocha', 'id_wfp', 'id_gadm', 'id_govt']
        res.extend([s + f'_{level}' for s in column_names])
    return res


def clean_adm(df, join, level):
    col_index = get_col_index()
    pcode = f'admin{level}Pcode'
    sub = join.filter(items=[pcode, f'id_{level}'])
    df = df.merge(sub, on=pcode, how='left')
    df = df.rename(columns={pcode: f'id_ocha_{level}'})
    cols = list(filter(lambda x: x in df.columns, col_index))
    df = df.reindex(cols, axis=1)
    df = df.drop_duplicates()
    return df


cwd = Path(__file__).parent
Path((cwd / '1_import_hdx').resolve()).mkdir(parents=True, exist_ok=True)
input_path = (cwd / '../data.csv').resolve()
for index, row in pd.read_csv(input_path).iterrows():
    if row['url'] is np.nan or not row['url'].startswith('https://data.humdata.org') or row['source'] == 'GADM':
        continue
    print(row['alpha_3'])
    hdx_file = f"../0_data_inputs/attributes/hdx/{row['alpha_3'].lower()}.xlsx"
    sheets = pd.ExcelFile((cwd / hdx_file).resolve())
    sheet_list = sorted(sheets.sheet_names)
    db = {'join': pd.DataFrame()}
    for sheet in sheet_list:
        df, level = parse_sheet(sheets, sheet)
        if level == 0:
            df = adm0_processing(df, db, row)
        else:
            df = admn_processing(df, db, level)
        db[f'adm{level}'] = df
    db['join'] = clean_join(db['join'], row)
    for sheet in db:
        if sheet != 'join':
            db[sheet] = clean_adm(db[sheet], db['join'], int(sheet[-1]))
    db['join'] = db['join'].filter(regex=r'^id_\d$')
    output = (cwd / f"1_import_hdx/{row['alpha_3'].lower()}.xlsx").resolve()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for key, value in db.items():
        value.to_excel(writer, sheet_name=key, startrow=1,
                       header=False, index=False)
        worksheet = writer.sheets[key]
        for idx, val in enumerate(value.columns):
            worksheet.write(0, idx, val)
    writer.save()
