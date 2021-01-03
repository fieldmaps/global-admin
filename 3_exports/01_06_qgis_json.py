import re
import json
from pathlib import Path
from sqlite3 import connect


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


def polygon_clip(batch, code, level, input, output):
    input = Path(f'{cwd}/00_import_boundless/{code}.gpkg')
    layer_1 = f'id_0_{code.upper()}'
    input_1 = (cwd_path /
               f'../0_data_inputs/boundaries/wld/{layer_1}.gpkg').resolve()
    for lvl in range(level + 1):
        layer_0 = f'adm{lvl}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "OVERLAY": f"'{input_1}|layername={layer_1}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def point_inaccessibility(batch, code, level, input, output):
    for lvl in range(level + 1):
        layer_0 = f'adm{lvl}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "TOLERANCE": "0.000001",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def polygon_to_lines(batch, code, level, input, output):
    input = Path(f'{cwd}/00_import_boundless/{code}.gpkg')
    for lvl in range(level + 1):
        layer_1 = f'adm{lvl}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_1}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_1}\" (geom) sql='",
            }
        })


def lines_dissolve(batch, code, level, input, output):
    layer_0 = 'adm0'
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer_0}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
        }
    })
    for lvl in range(1, level + 1):
        layer_1 = f'adm{lvl}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_1}'",
                "FIELD": f"['adm{lvl-1}_id']",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_1}\" (geom) sql='",
            }
        })


def lines_difference(batch, code, level, input, output):
    for lvl in range(1, level + 1):
        layer_1 = f'adm{lvl-1}'
        layer_0 = f'adm{lvl}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "OVERLAY": f"'{input}|layername={layer_1}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def lines_clip(batch, code, level, input, output):
    layer_1 = f'id_0_{code.upper()}'
    input_1 = (cwd_path /
               f'../0_data_inputs/boundaries/wld/{layer_1}.gpkg').resolve()
    for lvl in range(1, level + 1):
        layer_0 = f'adm{lvl}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "OVERLAY": f"'{input_1}|layername={layer_1}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


geo = [
    ('01_polygon_clip', polygon_clip, []),
    ('02_point_inaccessibility', point_inaccessibility, []),
    ('03_polygon_to_lines', polygon_to_lines, []),
    ('04_lines_dissolve', lines_dissolve, []),
    ('05_lines_difference', lines_difference, []),
    ('06_lines_clip', lines_clip, []),
]

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()
(cwd_path / 'qgis_json').mkdir(parents=True, exist_ok=True)

for item in geo:
    Path(cwd, item[0]).mkdir(parents=True, exist_ok=True)


bounds = (cwd_path / '00_import_boundless').resolve()
files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        print(code, level)
        for index, item in enumerate(geo):
            path, func, batch = item
            input = Path(f'{cwd}/{geo[index - 1][0]}/{code}.gpkg')
            output = Path(f'{cwd}/{path}/{code}.gpkg')
            func(batch, code, level, input, output)

for item in geo:
    path, func, batch = item
    with open(Path(f'{cwd}/qgis_json/{path}.json'), 'w') as outfile:
        json.dump(batch, outfile)
