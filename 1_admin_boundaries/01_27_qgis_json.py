import csv
import json
from pathlib import Path


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
            "error": f"''",
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


def final_higher(batch, code, level, path, layer, input, output):
    for l in range(level-1, -1, -1):
        layer_0 = f'{code}_adm{l}'
        layer_1 = f'{code}_adm{l+1}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{output}|layername={layer_1}'",
                "FIELD": f"['id_{l}']",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def final_higher_attr(batch, code, level, path, layer, input, output):
    batch = batch


def final_clip(batch, code, level, path, layer, input, output):
    layer_1 = f'id_0_{code.upper()}'
    input_1 = Path(f'{cwd}/00_inputs/wld/{layer_1}.gpkg')
    for l in range(level + 1):
        layer_0 = f'{code}_adm{l}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "OVERLAY": f"'{input_1}|layername={layer_1}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def lines_to_lines(batch, code, level, path, layer, input, output):
    for l in range(level + 1):
        layer_1 = f'{code}_adm{l}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_1}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_1}\" (geom) sql='",
            }
        })


def lines_difference(batch, code, level, path, layer, input, output):
    for l in range(level-1, -1, -1):
        layer_1 = f'{code}_adm{l}'
        layer_0 = f'{code}_adm{l+1}'
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "OVERLAY": f"'{input}|layername={layer_1}'",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def lines_clip(batch, code, level, path, layer, input, output):
    layer_1 = f'id_0_{code.upper()}'
    input_1 = Path(f'{cwd}/00_inputs/wld/{layer_1}.gpkg')
    for l in range(1, level + 1):
        layer_0 = f'{code}_adm{l}'
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
    ('20_final_higher', final_higher, []),
    ('21_final_higher_attr', final_higher_attr, []),
    ('22_final_clip', final_clip, []),
    ('25_lines_to_lines', lines_to_lines, []),
    ('26_lines_difference', lines_difference, []),
    ('27_lines_clip', lines_clip, []),
]

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()
Path(cwd, 'qgis_json').mkdir(parents=True, exist_ok=True)

for item in geo:
    Path(cwd, item[0]).mkdir(parents=True, exist_ok=True)

with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        for index, item in enumerate(geo):
            path, func, batch = item
            layer = f'{code}_adm{level}'
            input = Path(f'{cwd}/{geo[index - 1][0]}/{code}.gpkg')
            output = Path(f'{cwd}/{path}/{code}.gpkg')
            func(batch, code, level, path, layer, input, output)

for item in geo:
    path, func, batch = item
    with open(f'{cwd}/qgis_json/{path}.json', 'w') as outfile:
        json.dump(batch, outfile)
