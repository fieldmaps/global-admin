import os
import re
import pandas as pd
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent
bounds = (cwd / '02_point_inaccessibility').resolve()

output_path = (cwd / '07_refactor_points').resolve()
output_path.mkdir(parents=True, exist_ok=True)


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


def drop_fields(input, code: str, level: int):
    tmp = (output_path / f'{code}_tmp.gpkg').resolve()
    output = (output_path / f'{code}.gpkg').resolve()
    for level in range(level+1):
        print(code, level)
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM adm{level}" \
            -nln adm{level} \
            {'-append' if level > 0 else ''} \
            {tmp} {input}"""
        )
        conn = connect(tmp)
        df = pd.read_sql_query(f'SELECT * FROM "adm{level}"', conn)
        df = df.drop(columns=['dist_pole'])
        df.to_sql(f'adm{level}', conn, if_exists='replace', index=False)
        conn.close()
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM adm{level} ORDER BY adm{level}_id ASC" \
            -unsetFid \
            -nln adm{level} \
            {'-append' if level > 0 else ''} \
            {output} {tmp}"""
        )
        os.remove(tmp)


files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        drop_fields(in_file, code, level)
