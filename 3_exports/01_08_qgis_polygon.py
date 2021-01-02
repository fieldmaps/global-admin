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


def get_mappings(l):
    return [
        (f'id_{l}', f'adm{l}_id'),
        (f'id_ocha_{l}', f'adm{l}_ocha'),
        (f'name1_{l}', f'adm{l}_name1'),
        (f'name2_{l}', f'adm{l}_name2'),
        (f'name3_{l}', f'adm{l}_name3'),
        (f'namealt_{l}', f'adm{l}_namea'),
    ]


mappings_adm0 = [
    ('lang1', 'lang_name1', 10),
    ('lang2', 'lang_name2', 10),
    ('lang3', 'lang_name3', 10),
    ('src_name', 'src_name', 10),
    ('src_url', 'src_url', 10),
    ('src_date', 'src_date', 14),
    ('src_valid', 'src_valid', 14),
]


mappings_adm0_wfp = [
    ('id_wfp_0', 'wfp_id', 2),
    ('name_wfp', 'wfp_name', 10),
    ('name_wfp1', 'wfp_namea', 10),
    ('disp_area', 'wfp_disput', 10),
    ('source', 'wfp_source', 10),
    ('stscod', 'wfp_status', 10),
    ('map_lab', 'wfp_label', 10),
    ('mapclr', 'wfp_mapclr', 10),
    ('lst_update', 'wfp_update', 14),
]


def adm0_refactor(batch, code, level, input, output):
    input_a = Path(f'{cwd}/00_import_adm0/wld.gpkg')
    output_a = Path(f'{cwd}/01_adm0_refactor/wld.gpkg')
    input_p = Path(f'{cwd}/00_import_adm0/wld_points.gpkg')
    output_p = Path(f'{cwd}/01_adm0_refactor/wld_points.gpkg')
    input_groups = [(input_a, output_a, 0), (input_p, output_p, 1)]
    for input, output, index in input_groups:
        layer_0 = f'adm0'
        field_mapping = []
        for field in get_mappings(0):
            field_mapping.append({
                'expression': field[0], 'length': 0,
                'name': field[1], 'precision': 0, 'type': 10
            })
        for field in mappings_adm0:
            field_mapping.append({
                'expression': field[0], 'length': 0,
                'name': field[1], 'precision': 0, 'type': field[2]
            })
        for field in mappings_adm0_wfp:
            field_mapping.append({
                'expression': field[0], 'length': 0,
                'name': field[1], 'precision': 0, 'type': field[2]
            })
        batch[index] = {
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "FIELDS_MAPPING": f"{field_mapping}",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        }


def polygon_refactor(batch, code, level, input, output):
    input = Path(f'{cwd}/00_import_boundless/{code}.gpkg')
    for lvl in range(level + 1):
        layer_0 = f'adm{lvl}'
        field_mapping = []
        for l in range(lvl, -1, -1):
            for field in get_mappings(l):
                field_mapping.append({
                    'expression': field[0], 'length': 0,
                    'name': field[1], 'precision': 0, 'type': 10
                })
        for field in mappings_adm0:
            field_mapping.append({
                'expression': field[0], 'length': 0,
                'name': field[1], 'precision': 0, 'type': field[2]
            })
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "FIELDS_MAPPING": f"{field_mapping}",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


def polygon_clip(batch, code, level, input, output):
    layer_1 = f'id_0_{code.upper()}'
    input_1 = (cwd_path /
               f'../0_data_inputs/boundaries/wld_adm0/{layer_1}.gpkg').resolve()
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


def polygon_to_lines(batch, code, level, input, output):
    input = Path(f'{cwd}/01_polygon_refactor/{code}.gpkg')
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


def lines_refactor(batch, code, level, input, output):
    layer_0 = f'adm0'
    field_mapping = [{
        'expression': 'fid', 'length': 0,
        'name': 'fid', 'precision': 0, 'type': 4
    }]
    batch.append({
        "PARAMETERS": {
            "INPUT": f"'{input}|layername={layer_0}'",
            "FIELDS_MAPPING": f"{field_mapping}",
        },
        "OUTPUTS": {
            "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
        }
    })
    for lvl in range(1, level + 1):
        layer_1 = f'adm{lvl}'
        field_mapping = []
        for l in range(lvl-1, -1, -1):
            for field in get_mappings(l):
                field_mapping.append({
                    'expression': field[1], 'length': 0,
                    'name': field[1], 'precision': 0, 'type': 10
                })
        for field in mappings_adm0:
            field_mapping.append({
                'expression': field[1], 'length': 0,
                'name': field[1], 'precision': 0, 'type': field[2]
            })
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_1}'",
                "FIELDS_MAPPING": f"{field_mapping}",
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
               f'../0_data_inputs/boundaries/wld_adm0/{layer_1}.gpkg').resolve()
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


def pole_inaccessibility(batch, code, level, input, output):
    input = Path(f'{cwd}/02_polygon_clip/{code}.gpkg')
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


def point_refactor(batch, code, level, input, output):
    for lvl in range(level + 1):
        layer_0 = f'adm{lvl}'
        field_mapping = []
        for l in range(lvl, -1, -1):
            for field in get_mappings(l):
                field_mapping.append({
                    'expression': field[1], 'length': 0,
                    'name': field[1], 'precision': 0, 'type': 10
                })
        for field in mappings_adm0:
            field_mapping.append({
                'expression': field[1], 'length': 0,
                'name': field[1], 'precision': 0, 'type': field[2]
            })
        batch.append({
            "PARAMETERS": {
                "INPUT": f"'{input}|layername={layer_0}'",
                "FIELDS_MAPPING": f"{field_mapping}",
            },
            "OUTPUTS": {
                "OUTPUT": f"'ogr:dbname={output} table=\"{layer_0}\" (geom) sql='",
            }
        })


geo = [
    ('01_adm0_refactor', adm0_refactor, [{}, {}]),
    ('01_polygon_refactor', polygon_refactor, []),
    ('02_polygon_clip', polygon_clip, []),
    ('03_polygon_to_lines', polygon_to_lines, []),
    ('04_lines_dissolve', lines_dissolve, []),
    ('05_lines_refactor', lines_refactor, []),
    ('06_lines_difference', lines_difference, []),
    ('07_lines_clip', lines_clip, []),
    ('08_pole_inaccessibility', pole_inaccessibility, []),
    ('09_point_refactor', point_refactor, []),
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
