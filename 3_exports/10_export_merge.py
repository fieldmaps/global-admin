import os
import re
import shutil
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent
(cwd / '10_export_merge').mkdir(parents=True, exist_ok=True)

polygons = ((cwd / '01_adm0_refactor/wld.gpkg').resolve(),
            (cwd / '02_polygon_clip').resolve(),
            'polygons', 0)
lines = ((cwd / '../0_data_inputs/boundaries/wld_adm0_lines.gpkg').resolve(),
         (cwd / '07_lines_clip').resolve(),
         'lines', -1)
points = ((cwd / '01_adm0_refactor/wld_points.gpkg').resolve(),
          (cwd / '09_point_refactor').resolve(),
          'points', 0)


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


for template, bounds, layer, offset in [polygons, lines, points]:
    output = (cwd / f'10_export_merge/wld_{layer}.gpkg').resolve()
    shutil.copyfile(template, output)
    files_in_path = sorted(bounds.iterdir())
    for in_file in files_in_path:
        if in_file.is_file() and in_file.suffix == '.gpkg':
            code = in_file.name.split('.')[0]
            level = max_level_in_gpkg(in_file)
            for lvl in range(1, level + 1):
                print(code, lvl)
                os.system(
                    f"""ogr2ogr \
                    -sql 'SELECT * FROM adm{lvl} ORDER BY adm{lvl+offset}_id ASC' \
                    -unsetFid \
                    -nln adm{lvl} \
                    -append \
                    {output} {in_file}"""
                )
