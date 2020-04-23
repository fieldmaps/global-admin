from pathlib import Path
import pandas as pd
import numpy as np
from unidecode import unidecode


def get_levels(df):
    if not df.id_5.isnull().all():
        return [5, 4, 3, 2, 1]
    if not df.id_4.isnull().all():
        return [4, 3, 2, 1]
    if not df.id_3.isnull().all():
        return [3, 2, 1]
    if not df.id_2.isnull().all():
        return [2, 1]
    if not df.id_1.isnull().all():
        return [1]
    return []


def get_adm0(row, langs):
    df = pd.DataFrame()
    df.loc[0, 'id_0'] = row['id']
    for index, lang in enumerate(langs):
        df[f'admin0Name_{lang}'] = row[f'name_{index+1}']
    df['admin0Pcode'] = row['code_ocha']
    df['admin0RefName'] = unidecode(row['name_1'])
    for index, lang in enumerate(langs):
        if index == 0:
            df[f'admin0AltName1_{lang}'] = row['name_alt']
        else:
            df[f'admin0AltName1_{lang}'] = None
        df[f'admin0AltName2_{lang}'] = None
    df['date'] = row['src_date']
    df['date'] = df['date'].dt.date
    df['validOn'] = row['src_valid']
    df['validOn'] = df['validOn'].dt.date
    df['validTo'] = None
    return df


def format_adm(attr, row, level, langs):
    df = pd.DataFrame()
    df[f'id_{level}'] = attr['id']
    for index, lang in enumerate(langs):
        df[f'admin{level}Name_{lang}'] = attr[f'name_{index+1}']
    df[f'admin{level}Pcode'] = attr['code_ocha']
    df[f'admin{level}RefName'] = attr['name_1'].fillna(
        '').apply(lambda x: unidecode(x))
    for index, lang in enumerate(langs):
        if index == 0:
            df[f'admin{level}AltName1_{lang}'] = attr['name_alt']
        else:
            df[f'admin{level}AltName1_{lang}'] = None
        df[f'admin{level}AltName2_{lang}'] = None
    return df


def drop_col(join, level, max_level, langs):
    cols = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5']
    for lvl in range(max_level, -1, -1):
        if lvl == level:
            continue
        if lvl > level:
            for lang in langs:
                cols.append(f'admin{lvl}Name_{lang}')
            cols.append(f'admin{lvl}Pcode')
        cols.append(f'admin{lvl}RefName')
        for lang in langs:
            cols.append(f'admin{lvl}AltName1_{lang}')
            cols.append(f'admin{lvl}AltName2_{lang}')
    df = join.drop(columns=cols)
    df = df.dropna(subset=[f'admin{level}Pcode'])
    return df


na_values = ['', '#N/A']

cwd = Path(__file__).parent
input_path = (cwd / '1_merge_sources/wld.xlsx').resolve()
output_path = (cwd / '2_export_hdx/').resolve()
Path(output_path).mkdir(parents=True, exist_ok=True)

db = {}
print('Loading Global Admin xlsx...')
sheets = pd.ExcelFile(input_path)
print('Global Admin xlsx loaded')
for sheet in sheets.sheet_names:
    db[sheet] = sheets.parse(sheet_name=sheet, na_values=na_values,
                             keep_default_na=False)
print('Global Admin xlsx parsed')

for index, row in db['adm0'].iterrows():
    print(row['id'])
    cty = {}
    join = db['join'][db['join'].id_0.str.contains(row['id'], na=False)]
    langs_0 = [row['lang_1'], row['lang_2'], row['lang_3']]
    langs = list(filter(lambda x: x is not np.nan, langs_0))
    levels = get_levels(join)
    for level in levels:
        adm = f'adm{level}'
        attr = db[adm][db[adm].id.str.contains(row['id'], na=False)]
        lvl = format_adm(attr, row, level, langs)
        join = join.merge(lvl, how='outer', on=f'id_{level}')
    join = join.merge(get_adm0(row, langs), how='outer', on='id_0')
    drop_levels = levels + [0]
    for level in (drop_levels):
        cty[f'Admin{level}'] = drop_col(join, level, drop_levels[0], langs)
    ids = map(lambda x: f'id_{x}', range(5, drop_levels[0], -1))
    join = join.drop(columns=ids)
    cty['join'] = join

    output = f"2_export_hdx/{row['id'].lower()}.xlsx"
    writer = pd.ExcelWriter((cwd / output).resolve(), engine='xlsxwriter')
    for key, df in sorted(cty.items(), reverse=True):
        df.to_excel(writer, sheet_name=key, startrow=1,
                    header=False, index=False)
        worksheet = writer.sheets[key]
        for idx, val in enumerate(df.columns):
            worksheet.write(0, idx, val)
    writer.save()
