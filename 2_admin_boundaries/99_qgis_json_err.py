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


def point_surface(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/01_fix_geometry/{code}.gpkg')
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input_1}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def join_location(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/21_final_higher_attrs/{code}.gpkg')
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input_1}|layername={layer}'",
            'DISCARD_NONMATCHING': "False",
            'JOIN': f"'{input}|layername={layer}'",
            'JOIN_FIELDS': "[]",
            'METHOD': "2",
            'PREDICATE': "[1]",
            'PREFIX': "''"
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
            "NON_MATCHING": f"'ogr:dbname={output} table=\"{layer}_err\" (geom) sql='",
        }
    })


def refactor_fields(batch, code, level, path, layer, input, output):
    result = []
    for l in range(level + 1):
        expression = {
            "expression": f'"id_{l}_2"',
            "length": "0",
            "name": f"id_{l}",
            "precision": "0",
            "type": "10",
        }
        result.append(expression)
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
            'FIELDS_MAPPING': f"{result}",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


geo = [
    ('99_1_point_surface', point_surface, []),
    ('99_2_join_location', join_location, []),
    ('99_3_refactor_fields', refactor_fields, []),
]

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()
(cwd_path / 'qgis_json_err').mkdir(parents=True, exist_ok=True)

for item in geo:
    Path(cwd, item[0]).mkdir(parents=True, exist_ok=True)


bounds = (cwd_path / '01_fix_geometry').resolve()
files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        print(code, level)
        for index, item in enumerate(geo):
            path, func, batch = item
            layer = f'{code}_adm{level}'
            input = Path(f'{cwd}/{geo[index - 1][0]}/{code}.gpkg')
            output = Path(f'{cwd}/{path}/{code}.gpkg')
            func(batch, code, level, path, layer, input, output)

for item in geo:
    path, func, batch = item
    with open(Path(f'{cwd}/qgis_json_err/{path}.json'), 'w') as outfile:
        json.dump(batch, outfile)
