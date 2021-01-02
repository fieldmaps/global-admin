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


def fix_geometry(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/00_inputs/{code}.gpkg')
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input_1}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def admin_dissolve(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def admin_to_lines(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/{geo[0][0]}/{code}.gpkg')
    input_2 = Path(f'{cwd}/{geo[1][0]}/{code}.gpkg')
    output_1 = Path(f'{cwd}/{geo[2][0]}/{code}_1.gpkg')
    output_2 = Path(f'{cwd}/{geo[2][0]}/{code}_2.gpkg')
    loop = [(input_1, output_1), (input_2, output_2)]
    for input_0, output_0 in loop:
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input_0}|layername={layer}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output_0} table=\"{layer}\" (geom) sql='",
            }
        })


def admin_intersect(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/{geo[2][0]}/{code}_1.gpkg')
    input_2 = Path(f'{cwd}/{geo[2][0]}/{code}_2.gpkg')
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input_1}|layername={layer}'",
            "OVERLAY": f"'{input_2}|layername={layer}'",
            "OVERLAY_FIELDS": "['id_0']",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def outline_buffer(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
            "DISTANCE": "0.000001",
            "SEGMENTS": "10",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def outline_to_lines(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def corner_line_intersect(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/{geo[3][0]}/{code}.gpkg')
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input_1}|layername={layer}'",
            "INTERSECT": f"'{input}|layername={layer}'",
            'INTERSECT_FIELDS': "['id_0']",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def corner_buffer(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
            "DISTANCE": "0.000002",
            "SEGMENTS": "10",
            "DISSOLVE": "True",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def outline_difference(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/{geo[3][0]}/{code}.gpkg')
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input_1}|layername={layer}'",
            "OVERLAY": f"'{input}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def outline_explode(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def outline_centroid(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def points_merge(batch, code, level, path, layer, input, output):
    batch = batch


def voronoi_generate(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
            "BUFFER": "100",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def voronoi_dissolve(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
            "FIELD": f"['id_{level}']",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def final_union(batch, code, level, path, layer, input, output):
    input_1 = Path(f'{cwd}/{geo[0][0]}/{code}.gpkg')
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input_1}|layername={layer}'",
            "OVERLAY": f"'{input}|layername={layer}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def final_attributes(batch, code, level, path, layer, input, output):
    batch = batch


def final_dissolve(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer}'",
            "FIELD": f"['id_{level}']",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def final_clean(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "input": f"'{input}|layername={layer}'",
            "type": "[2]",
            "tool": "[1]",
            "threshold": "''",
            "-b": "False",
            "-c": "False",
            "GRASS_REGION_PARAMETER": "None",
            "GRASS_SNAP_TOLERANCE_PARAMETER": "0.000001",
            "GRASS_MIN_AREA_PARAMETER": "0.0001",
            "GRASS_OUTPUT_TYPE_PARAMETER": "0",
            "GRASS_VECTOR_DSCO": "''",
            "GRASS_VECTOR_LCO": "''",
            "GRASS_VECTOR_EXPORT_NOCAT": "False"
        },
        "OUTPUTS": {
            "output": f"'{output}'",
            "error": f"'{output}.err'",
        }
    })


def final_fix(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}'",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer}\" (geom) sql='",
        }
    })


def final_higher_dissolve(batch, code, level, path, layer, input, output):
    for l in range(level, -1, -1):
        layer_0 = f'{code}_adm{l}'
        layer_1 = f'{code}_adm{l+1}'
        input_0 = output
        if l == level:
            input_0 = Path(f'{cwd}/{geo[18][0]}/{code}.gpkg')
            layer_1 = f'{code}_adm{l}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input_0}|layername={layer_1}'",
                "FIELD": f"['id_{l}']",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def final_higher_attr(batch, code, level, path, layer, input, output):
    batch = batch


geo = [
    ('01_fix_geometry', fix_geometry, []),
    ('02_admin_dissolve', admin_dissolve, []),
    ('03_admin_to_lines', admin_to_lines, []),
    ('04_admin_intersect', admin_intersect, []),
    ('05_outline_buffer', outline_buffer, []),
    ('06_outline_to_lines', outline_to_lines, []),
    ('07_corner_line_intersect', corner_line_intersect, []),
    ('08_corner_buffer', corner_buffer, []),
    ('09_outline_difference', outline_difference, []),
    ('10_outline_explode', outline_explode, []),
    ('11_outline_centroid', outline_centroid, []),
    ('12_points_merge', points_merge, []),
    ('13_voronoi_generate', voronoi_generate, []),
    ('14_voronoi_dissolve', voronoi_dissolve, []),
    ('15_final_union', final_union, []),
    ('16_final_attributes', final_attributes, []),
    ('17_final_dissolve', final_dissolve, []),
    ('18_final_clean', final_clean, []),
    ('19_final_fix', final_fix, []),
    ('20_final_higher_dissolve', final_higher_dissolve, []),
    ('21_final_higher_attrs', final_higher_attr, []),
]

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()
(cwd_path / 'qgis_json').mkdir(parents=True, exist_ok=True)

for item in geo:
    Path(cwd, item[0]).mkdir(parents=True, exist_ok=True)


bounds = (cwd_path / '00_inputs').resolve()
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
    with open(Path(f'{cwd}/qgis_json/{path}.json'), 'w') as outfile:
        json.dump(batch, outfile)
