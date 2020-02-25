import os
import csv
import json
from pathlib import Path


def fix_geometry(batch, code, level, path, layer, output):
    input_1 = Path('{0}/input/boundaries/{1}.gpkg'.format(cwd, code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def admin_dissolve(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[0][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def admin_to_lines(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[0][0], code))
    input_2 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[1][0], code))
    output_1 = Path('{0}/tmp/{1}/{2}_1.gpkg'.format(cwd, geo[2][0], code))
    output_2 = Path('{0}/tmp/{1}/{2}_2.gpkg'.format(cwd, geo[2][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output_1, layer)
        }
    })
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_2, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output_2, layer)
        }
    })


def admin_intersect(batch, code, level, path, layer, output):
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


def outline_buffer(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[3][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "DISTANCE": "0.000001",
            "SEGMENTS": "100",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def outline_to_lines(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[4][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
        }
    })


def corner_line_intersect(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[3][0], code))
    input_2 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[5][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "INTERSECT": "'{0}|layername={1}'".format(input_2, layer),
            'INTERSECT_FIELDS': "['admin0Pcode']",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def corner_buffer(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[6][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "DISTANCE": "0.000002",
            "DISSOLVE": "True",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def vertices_extract(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[3][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def vertices_difference(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[8][0], code))
    input_2 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[7][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "OVERLAY": "'{0}|layername={1}'".format(input_2, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def admin_line_explode(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[3][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def admin_line_centroid(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[10][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def vertices_merge(batch, code, level, path, layer, output):
    batch = batch


def voronoi_generate(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[12][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "BUFFER": "100",
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def voronoi_dissolve(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[13][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "FIELD": "['admin{0}Pcode']".format(level),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def voronoi_holes(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[14][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def voronoi_difference(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[15][0], code))
    input_2 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[0][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "OVERLAY": "'{0}|layername={1}'".format(input_2, layer),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def final_merge(batch, code, level, path, layer, output):
    batch = batch


def final_dissolve(batch, code, level, path, layer, output):
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[17][0], code))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "FIELD": "['admin{0}Pcode']".format(level),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer),
        }
    })


def final_clip(batch, code, level, path, layer, output):
    layer_2 = 'ISO3CD_{0}'.format(code.upper())
    input_1 = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, geo[18][0], code))
    input_2 = Path('{0}/input/world/{1}.gpkg'.format(cwd, layer_2))
    batch.append({
        "PARAMETERS": {
            "INPUT": "'{0}|layername={1}'".format(input_1, layer),
            "OVERLAY": "'{0}|layername={1}'".format(input_2, layer_2),
        },
        "OUTPUTS": {
            "OUTPUT": "'ogr:dbname={0} table=\"{1}\" (geom) sql='".format(output, layer)
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
    ('08_vertices_extract', vertices_extract, []),
    ('09_vertices_difference', vertices_difference, []),
    ('10_admin_line_explode', admin_line_explode, []),
    ('11_admin_line_centroid', admin_line_centroid, []),
    ('12_vertices_merge', vertices_merge, []),
    ('13_voronoi_generate', voronoi_generate, []),
    ('14_voronoi_dissolve', voronoi_dissolve, []),
    ('15_voronoi_holes', voronoi_holes, []),
    ('16_voronoi_difference', voronoi_difference, []),
    ('17_final_merge', final_merge, []),
    ('18_final_dissolve', final_dissolve, []),
    ('19_final_clip', final_clip, []),
    # ('19_higher_dissolve', higher_dissolve, []),
]

Path('tmp').mkdir(parents=True, exist_ok=True)
Path('qgis').mkdir(parents=True, exist_ok=True)

for item in geo:
    Path('tmp/' + item[0]).mkdir(parents=True, exist_ok=True)

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        for item in geo:
            path, func, batch = item
            layer = '{0}_adm{1}'.format(code, level)
            output = Path('{0}/tmp/{1}/{2}.gpkg'.format(cwd, path, code))
            func(batch, code, level, 'tmp/' + path, layer, output)

for item in geo:
    path, func, batch = item
    with open('{0}/qgis/{1}.json'.format(cwd, path), 'w') as outfile:
        json.dump(batch, outfile)
