import os
import csv
import json
import shutil
from pathlib import Path


def merge_layers(code, level):
    input_1 = Path('{0}/tmp/10_outline_centroid/{1}.gpkg'.format(cwd, code))
    input_2 = Path('{0}/tmp/11_outline_along/{1}.gpkg'.format(cwd, code))
    input_3 = Path(
        '{0}/tmp/06_corner_line_intersect/{1}.gpkg'.format(cwd, code))
    output = Path('{0}/tmp/12_points_merge/{1}.gpkg'.format(cwd, code))
    if os.path.isfile(input_1) and os.path.isfile(input_2) and os.path.isfile(input_3):
        shutil.copyfile(input_1, output)
        os.system("ogr2ogr -f 'gpkg' -append {0} {1}".format(output, input_2))
        os.system("ogr2ogr -f 'gpkg' -append {0} {1}".format(output, input_3))


cwd = os.getcwd()

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        merge_layers(code, level)
