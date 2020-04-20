import os
import csv
import json
from pathlib import Path


def fix_geometry(batch, code, level, path, layer, input, output):
    input_1 = Path('{0}/inputs/{1}.gpkg'.format(cwd, code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def admin_dissolve(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def admin_to_lines(batch, code, level, path, layer, input, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[0][0], code))
    input_2 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[1][0], code))
    output_1 = Path('{0}/tmp/{1}/{2}_1.gpkg'.format(cwd, geo[2][0], code))
    output_2 = Path('{0}/tmp/{1}/{2}_2.gpkg'.format(cwd, geo[2][0], code))
    loop = [(input_1, output_1), (input_2, output_2)]
    for input_0, output_0 in loop:
        batch.append({
            "PARAMETERS": {
                "INPUT": "'{0}|layername={1}'".format(input_0, layer),
            },
            "OUTPUTS": {
                "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output_0, layer)
            }
        })


def admin_intersect(batch, code, level, path, layer, input, output):
    input_1 = Path('{0}/tmp/{1}/{2}_1.gpkg'.format(cwd, geo[2][0], code))
    input_2 = Path('{0}/tmp/{1}/{2}_2.gpkg'.format(cwd, geo[2][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "OVERLAY": "'{0}|layername={1}'".format(input_2, layer),
            "OVERLAY_FIELDS": "['admin0Pcode']",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def outline_buffer(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
            "DISTANCE": "0.000001",
            "SEGMENTS": "10",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def outline_to_lines(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def corner_line_intersect(batch, code, level, path, layer, input, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[3][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "INTERSECT": "'{0}|layername={1}'".format(input, layer),
            'INTERSECT_FIELDS': "['admin0Pcode']",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def corner_buffer(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
            "DISTANCE": "0.000002",
            "SEGMENTS": "10",
            "DISSOLVE": "True",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def outline_difference(batch, code, level, path, layer, input, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[3][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "OVERLAY": "'{0}|layername={1}'".format(input, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def outline_explode(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def outline_centroid(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def outline_along(batch, code, level, path, layer, input, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[8][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "DISTANCE": "0.001",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def points_merge(batch, code, level, path, layer, input, output):
    batch = batch


def voronoi_generate(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
            "BUFFER": "100",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def voronoi_dissolve(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
            "FIELD": "['admin{0}Pcode']".format(level),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def final_union(batch, code, level, path, layer, input, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[0][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "OVERLAY": "'{0}|layername={1}'".format(input, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def final_attributes(batch, code, level, path, layer, input, output):
    batch = batch


def final_dissolve(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
            "FIELD": "['admin{0}Pcode']".format(level),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def final_clean(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "input": "'{0}|layername={1}'".format(input, layer),
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
            "output": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
            "error": "'ogr:dbname={0} table=\"{1}_err\" (geom) sql='".format(output, layer),
        }
    })


def final_fix(batch, code, level, path, layer, input, output):
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def final_higher(batch, code, level, path, layer, input, output):
    for l in levels[level]:
        layer_0 = '{0}_adm{1}'.format(code, l)
        batch.append({
            "PARAMETERS": {
                "INPUT": "'{0}|layername={1}'".format(input, layer),
                "FIELD": "['admin{0}Pcode']".format(l),
            },
            "OUTPUTS": {
                "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer_0)
            }
        })


def final_higher_attr(batch, code, level, path, layer, input, output):
    batch = batch


def final_clip(batch, code, level, path, layer, input, output):
    layer_1 = 'ISO3CD_{0}'.format(code.upper())
    input_1 = Path('{0}/input/world/{1}.gpkg'.format(cwd, layer_1))
    for l in levels[level]:
        layer_0 = '{0}_adm{1}'.format(code, l)
        batch.append({
            "PARAMETERS": {
                "INPUT": "'{0}|layername={1}'".format(input, layer_0),
                "OVERLAY": "'{0}|layername={1}'".format(input_1, layer_1),
            },
            "OUTPUTS": {
                "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer_0)
            }
        })


def final_clip_alt(batch, code, level, path, layer, input, output):
    layer_1 = 'iso3_{0}'.format(code.upper())
    input_1 = Path('{0}/input/world_wfp/{1}.gpkg'.format(cwd, layer_1))
    for l in levels[level]:
        layer_0 = '{0}_adm{1}'.format(code, l)
        batch.append({
            "PARAMETERS": {
                "INPUT": "'{0}|layername={1}'".format(input, layer_0),
                "OVERLAY": "'{0}|layername={1}'".format(input_1, layer_1),
            },
            "OUTPUTS": {
                "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer_0)
            }
        })


cwd = os.getcwd()
geo = [
    ('00_fix_geometry', fix_geometry, []),
    ('01_admin_dissolve', admin_dissolve, []),
    ('02_admin_to_lines', admin_to_lines, []),
    ('03_admin_intersect', admin_intersect, []),
    ('04_outline_buffer', outline_buffer, []),
    ('05_outline_to_lines', outline_to_lines, []),
    ('06_corner_line_intersect', corner_line_intersect, []),
    ('07_corner_buffer', corner_buffer, []),
    ('08_outline_difference', outline_difference, []),
    ('09_outline_explode', outline_explode, []),
    ('10_outline_centroid', outline_centroid, []),
    ('11_outline_along', outline_along, []),
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
    ('22_final_clip_alt', final_clip_alt, []),
]

levels = {
    '5': [5, 4, 3, 2, 1, 0],
    '4': [4, 3, 2, 1, 0],
    '3': [3, 2, 1, 0],
    '2': [2, 1, 0],
    '1': [1, 0],
    '0': [0],
}

Path('tmp').mkdir(parents=True, exist_ok=True)
Path('qgis').mkdir(parents=True, exist_ok=True)

for item in geo:
    Path('tmp/' + item[0]).mkdir(parents=True, exist_ok=True)

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        for index, item in enumerate(geo):
            path, func, batch = item
            layer = '{0}_adm{1}'.format(code, level)
            input = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd,
                                                       geo[index - 1][0], code))
            output = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, path, code))
            func(batch, code, level, 'tmp/' + path, layer, input, output)

for item in geo:
    path, func, batch = item
    with open('{0}/qgis/{1}.json'.format(cwd, path), 'w') as outfile:
        json.dump(batch, outfile)
