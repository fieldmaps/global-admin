import os
import csv
import json
import shutil
from pathlib import Path


def merge_layers(code, level):
    input_1 = Path('{0}/tmp/01_admin_clip/{1}.gpkg'.format(cwd, code))
    input_2 = Path('{0}/tmp/15_voronoi_clip/{1}.gpkg'.format(cwd, code))
    output = Path('{0}/tmp/16_final_merge/{1}.gpkg'.format(cwd, code))
    if os.path.isfile(input_2):
        shutil.copyfile(input_1, output)
        os.system("ogr2ogr -f 'gpkg' -append {0} {1}".format(output, input_2))


cwd = os.getcwd()

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['iso_3']
        level = row['admin_level_full']
        merge_layers(code, level)
