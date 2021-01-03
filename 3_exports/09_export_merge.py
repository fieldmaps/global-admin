import os
import re
import shutil
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent

output_path = (cwd / '09_export_merge').resolve()
shutil.rmtree(output_path, ignore_errors=True)
output_path.mkdir(parents=True, exist_ok=True)

polygons = ((cwd / '00_import_adm0/wld_polygons.gpkg').resolve(),
            (cwd / '01_polygon_clip').resolve(),
            'polygons', 0)
points = ((cwd / '00_import_adm0/wld_points.gpkg').resolve(),
          (cwd / '07_refactor_points').resolve(),
          'points', 0)
lines = ((cwd / '../0_data_inputs/boundaries/wld_lines.gpkg').resolve(),
         (cwd / '08_refactor_lines').resolve(),
         'lines', -1)


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


for template, bounds, layer, offset in [polygons, points, lines]:
    output = (output_path / f'wld_{layer}.gpkg').resolve()
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
