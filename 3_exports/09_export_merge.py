import os
import re
import shutil
import pandas as pd
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent

output_path = (cwd / '09_export_merge').resolve()
output_path.mkdir(parents=True, exist_ok=True)

points = ((cwd / '00_import_adm0/wld_points.gpkg').resolve(),
          (cwd / '07_refactor_points').resolve(),
          'points', 0)
lines = ((cwd / '../0_data_inputs/boundaries/wld_lines.gpkg').resolve(),
         (cwd / '08_refactor_lines').resolve(),
         'lines', -1)
polygons = ((cwd / '00_import_adm0/wld_polygons.gpkg').resolve(),
            (cwd / '01_polygon_clip').resolve(),
            'polygons', 0)


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


for template, bounds, layer, offset in [points, lines, polygons]:
    tmp = (output_path / f'wld_{layer}_tmp.gpkg').resolve()
    output = (output_path / f'wld_{layer}.gpkg').resolve()
    df_a = pd.DataFrame(columns=['adm0_id', 'adm_max'])
    shutil.copyfile(template, tmp)
    files_in_path = sorted(bounds.iterdir())
    for in_file in files_in_path:
        if in_file.is_file() and in_file.suffix == '.gpkg':
            code = in_file.name.split('.')[0]
            level = max_level_in_gpkg(in_file)
            df_a = df_a.append({'adm0_id': code.upper(), 'adm_max': level},
                               ignore_index=True)
            for lvl in range(1, level + 1):
                print(code, lvl)
                os.system(
                    f"""ogr2ogr \
                    -sql 'SELECT * FROM adm{lvl} ORDER BY adm{lvl+offset}_id ASC' \
                    -unsetFid \
                    -nln adm{lvl} \
                    -append \
                    {tmp} {in_file}"""
                )
    conn = connect(tmp)
    for level in range(5):
        if layer != 'lines' or level != 0:
            df = pd.read_sql_query(f'SELECT * FROM adm{level}', conn)
            df = df.merge(df_a, on='adm0_id', how='left')
            df = df.fillna({'adm_max': 0})
            df.to_sql(f'adm{level}', conn, if_exists='replace', index=False)
    conn.close()
    os.system(f'ogr2ogr {output} {tmp}')
    os.remove(tmp)
