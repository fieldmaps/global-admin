from pathlib import Path
import pandas as pd
import shutil
from sqlite3 import connect


cwd = Path(__file__).parent
(cwd / '1_import_hdx').mkdir(parents=True, exist_ok=True)
input_path = (cwd / '../0_data_inputs/attributes/hdx').resolve()
output_path = (cwd / '1_import_hdx').resolve()
shutil.rmtree(output_path, ignore_errors=True)
output_path.mkdir(parents=True, exist_ok=True)

ocha_cod = pd.read_csv((cwd / '../ocha-cod.csv').resolve())
country_codes = pd.read_csv((cwd / '../country-codes.csv').resolve())
ocha_cod = ocha_cod.merge(country_codes, left_on='ISO 3166-1 Alpha 3-Codes',
                          right_on='alpha-3')


def parse_sheet(sheets, sheet):
    level = int(sheet[-1])
    na_values = ['', '#N/A']
    df = sheets.parse(sheet_name=sheet, na_values=na_values,
                      keep_default_na=False)
    df = df.replace(regex=r'^\s+$', value=None)
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


def adm0_processing(df, db):
    df = df.merge(ocha_cod, left_on='admin0Pcode',
                  right_on='alpha-2', how='left')
    new_date = {'date': 'src_date', 'validOn': 'src_valid',
                'COD-AB URL': 'src_url'}
    re_adm0 = r'^admin0Pcode|^admin0Name_|^admin0AltName_|^date$|^validOn$|^COD-AB URL$'
    df = df.filter(regex=re_adm0)
    df = rename_lang(df, 0)
    df['src_name'] = 'OCHA'
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


def clean_join(df, code):
    for col in df.columns:
        if col == 'admin0Pcode':
            df['id_0'] = code
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
    res = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4',
           'src_name', 'src_url', 'src_date', 'src_valid', 'lang1', 'lang2', 'lang3']
    for level in range(5):
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


files_in_path = sorted(input_path.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.xlsx':
        code = in_file.name.split('.')[0]
        print(code)
        sheets = pd.ExcelFile(in_file, engine='openpyxl')
        sheet_list = sorted(sheets.sheet_names)
        db = {'join': pd.DataFrame()}
        for sheet in sheet_list:
            df, level = parse_sheet(sheets, sheet)
            if level == 0:
                df = adm0_processing(df, db)
            else:
                df = admn_processing(df, db, level)
            db[f'adm{level}'] = df
        db['join'] = clean_join(db['join'], code.upper())
        for sheet in db:
            if sheet != 'join':
                db[sheet] = clean_adm(db[sheet], db['join'], int(sheet[-1]))
        db['join'] = db['join'].filter(regex=r'^id_\d$')
        output = (output_path / f'{code}.db').resolve()
        conn = connect(output)
        for table, df in db.items():
            if table != 'join' and not df[f'id_{table[-1]}'].is_unique:
                raise ValueError(f'Duplicate ID value in {table}')
            df.to_sql(table, conn, index=False)
        conn.close()
