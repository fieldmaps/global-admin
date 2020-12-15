from pathlib import Path
import pandas as pd
import numpy as np
import shutil
from unidecode import unidecode
from sqlite3 import connect


def tables_in_sqlite_db(conn):
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    return tables


def get_levels(df):
    if not df['id_4'].isna().all():
        return [4, 3, 2, 1]
    if not df['id_3'].isna().all():
        return [3, 2, 1]
    if not df['id_2'].isna().all():
        return [2, 1]
    if not df['id_1'].isna().all():
        return [1]
    return []


def get_adm0(row, langs):
    df = pd.DataFrame()
    df.loc[0, 'id_0'] = row['id_0']
    for index, lang in enumerate(langs):
        df[f'admin0Name_{lang}'] = row[f'name{index+1}_0']
    df['admin0Pcode'] = row['id_ocha_0']
    df['admin0RefName'] = unidecode(row['name1_0'])
    for index, lang in enumerate(langs):
        if index == 0:
            df[f'admin0AltName1_{lang}'] = row['namealt_0']
        else:
            df[f'admin0AltName1_{lang}'] = None
        df[f'admin0AltName2_{lang}'] = None
    df['date'] = row['src_date']
    df['date'] = df['date']
    df['validOn'] = row['src_valid']
    df['validOn'] = df['validOn']
    df['validTo'] = None
    return df


def format_adm(attr, row, level, langs):
    df = pd.DataFrame()
    df[f'id_{level}'] = attr[f'id_{level}']
    for index, lang in enumerate(langs):
        df[f'admin{level}Name_{lang}'] = attr[f'name{index+1}_{level}']
    df[f'admin{level}Pcode'] = attr[f'id_ocha_{level}']
    df[f'admin{level}RefName'] = attr[f'name1_{level}'].fillna(
        '').apply(lambda x: unidecode(x))
    for index, lang in enumerate(langs):
        if index == 0:
            df[f'admin{level}AltName1_{lang}'] = attr[f'namealt_{level}']
        else:
            df[f'admin{level}AltName1_{lang}'] = None
        df[f'admin{level}AltName2_{lang}'] = None
    return df


def drop_col(join, level, max_level, langs):
    cols = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4']
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


cwd = Path(__file__).parent
input_path = (cwd / '2_merge_sources/wld.db').resolve()
output_path = (cwd / '3_export_hdx/').resolve()
shutil.rmtree(output_path, ignore_errors=True)
output_path.mkdir(parents=True, exist_ok=True)

db = {}
print('Loading Global Admin DB...')
conn = connect(input_path)
tables = tables_in_sqlite_db(conn)
for table in tables:
    db[table] = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
conn.close()
print('Global Admin DB loaded')

for index, row in db['adm0'].iterrows():
    print(row['id_0'])
    cty = {}
    join = db['join'][db['join']['id_0'].str.contains(row['id_0'], na=False)]
    langs_0 = [row['lang1'], row['lang2'], row['lang3']]
    langs = list(filter(lambda x: x is not np.nan, langs_0))
    levels = get_levels(join)
    for level in levels:
        adm = f'adm{level}'
        attr = db[adm][db[adm][f'id_{level}'].str.contains(
            row['id_0'], na=False)]
        lvl = format_adm(attr, row, level, langs)
        join = join.merge(lvl, how='outer', on=f'id_{level}')
    join = join.merge(get_adm0(row, langs), how='outer', on='id_0')
    drop_levels = levels + [0]
    for level in (drop_levels):
        cty[f'Admin{level}'] = drop_col(join, level, drop_levels[0], langs)
    ids = map(lambda x: f'id_{x}', range(4, drop_levels[0], -1))
    join = join.drop(columns=ids)
    cty['join'] = join

    output = f"3_export_hdx/{row['id_0'].lower()}.xlsx"
    writer = pd.ExcelWriter((cwd / output).resolve(), engine='openpyxl')
    for key, df in sorted(cty.items(), reverse=True):
        df.to_excel(writer, sheet_name=key, index=False)
    writer.save()
