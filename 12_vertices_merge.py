import os
import csv
import json
import shutil
from pathlib import Path


def merge_layers(code, level):
    input_1 = Path('{0}/tmp/10_vertices_extract/{1}.gpkg'.format(cwd, code))
    input_2 = Path(
        '{0}/tmp/08_corner_line_intersect/{1}.gpkg'.format(cwd, code))
    output = Path('{0}/tmp/12_vertices_merge/{1}.gpkg'.format(cwd, code))
    if os.path.isfile(input_1):
        shutil.copyfile(input_1, output)
        os.system("ogr2ogr -f 'gpkg' -append {0} {1}".format(output, input_2))


cwd = os.getcwd()

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        merge_layers(code, level)
