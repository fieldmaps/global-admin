from pathlib import Path
import pandas as pd


def col_str(df, col):
    if col in df.columns:
        df[col] = df[col].fillna('')
        df[col] = df[col].apply(str)
    return df


def get_col_index():
    res = ['id_0', 'id_1', 'id_2', 'id_3', 'id_4', 'id_5',
           'src_name', 'src_url', 'src_date', 'src_valid', 'lang1', 'lang2', 'lang3']
    for level in range(6):
        column_names = ['name1', 'name2', 'name3', 'namealt',
                        'type1', 'type2', 'type3', 'typealt', 'id_ocha', 'id_gadm', 'id_govt']
        res.extend([s + f'_{level}' for s in column_names])
    return res


def get_converters():
    res = {}
    items = ['name1', 'name2', 'name3', 'namealt',
             'type1', 'typealt', 'id_govt', 'id_ocha']
    for lvl in range(6):
        for item in items:
            res[f'{item}_{lvl}'] = str
    return res


col_index = get_col_index()
na_values = ['', '#N/A']
output = {}

cwd = Path(__file__).parent
output_path = (cwd / '2_merge_sources').resolve()
Path(output_path).mkdir(parents=True, exist_ok=True)

hdx_list = list((cwd / '1_import_hdx').resolve().glob('*.xlsx'))
hdx_list_2 = map(lambda x: str(x)[-8:-5], hdx_list)

govt_list = list((cwd / '1_import_govt').resolve().glob('*.xlsx'))
govt_list_2 = map(lambda x: str(x)[-8:-5], govt_list)

gadm_list = map(lambda x: str(x)[-8:-5],
                (cwd / '1_import_gadm').resolve().glob('*.xlsx'))
gadm_list_2 = set(gadm_list).difference(hdx_list_2)
gadm_list_2 = set(gadm_list_2).difference(govt_list_2)
gadm_list_3 = filter(lambda x: str(x)[0] != 'x', gadm_list_2)
gadm_list_4 = map(lambda x: (
    cwd / f'1_import_gadm/{x}.xlsx').resolve(), gadm_list_3)
all_list = sorted(hdx_list + govt_list + list(gadm_list_4))

for path in all_list:
    print(path)
    sheets = pd.ExcelFile(path)
    for sheet in sheets.sheet_names:
        df = sheets.parse(sheet_name=sheet, converters=get_converters(),
                          na_values=na_values, keep_default_na=False)
        if sheet != 'join':
            level = int(sheet[-1])
            if level == 0:
                df['src_date'] = pd.to_datetime(df['src_date'])
            df = col_str(df, f'name1_{level}')
            df = col_str(df, f'name2_{level}')
            df = col_str(df, f'name3_{level}')
            df = col_str(df, f'namealt_{level}')
            df = col_str(df, f'type1_{level}')
            df = col_str(df, f'typealt_{level}')
            df = col_str(df, f'id_govt_{level}')
            df = col_str(df, f'id_ocha_{level}')
        if sheet in output:
            output[sheet] = output[sheet].merge(df, how='outer')
        else:
            output[sheet] = df

output_path = '2_merge_sources/wld.xlsx'
writer = pd.ExcelWriter((cwd / output_path).resolve(), engine='xlsxwriter')
for key, df in output.items():
    print(key)
    if key == 'adm0':
        df['src_valid'] = df['src_valid'].dt.date
        df['src_date'] = df['src_date'].dt.date
    if key != 'join' and not df[f'id_{int(key[-1])}'].is_unique:
        raise ValueError('Duplicate ID value')
    cols = list(filter(lambda x: x in df.columns, col_index))
    df = df.reindex(cols, axis=1)
    df = df.sort_values(by=cols)
    df.to_excel(writer, sheet_name=key, startrow=1, header=False, index=False)
    worksheet = writer.sheets[key]
    for idx, val in enumerate(df.columns):
        worksheet.write(0, idx, val)
writer.save()
