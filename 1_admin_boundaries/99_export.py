import os
import csv
import json
import shutil
from pathlib import Path


def merge_adm(source, code, max, curr):
    level = curr if curr <= max else max
    input = Path(
        '{0}/tmp/22_final_clip_{2}/{1}.gpkg'.format(cwd, code, source))
    output = Path('{0}/output/wld_{1}.gpkg'.format(cwd, source))
    os.system(
        "ogr2ogr -f 'gpkg' -append -sql 'SELECT * FROM {2}_adm{3}' -nln wld_adm{4} {0} {1}".format(
            output, input, code, level, curr))


def merge_disp(source, level):
    input = Path('{0}/input/world_disputed_{1}.gpkg'.format(cwd, source))
    output = Path('{0}/output/wld_{1}.gpkg'.format(cwd, source))
    os.system(
        "ogr2ogr -f 'gpkg' -append -sql 'SELECT * FROM wld_adm0' -nln wld_adm{2} {0} {1}".format(
            output, input, level))


cwd = os.getcwd()

with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for source in ['un', 'wfp']:
        for row in reader:
            code = row['iso_3']
            max = int(row['admin_level_full'])
            merge_adm(source, code, max, 4)
            merge_adm(source, code, max, 3)
            merge_adm(source, code, max, 2)
            merge_adm(source, code, max, 1)
            merge_adm(source, code, max, 0)
        merge_disp(source, 4)
        merge_disp(source, 3)
        merge_disp(source, 2)
        merge_disp(source, 1)
        merge_disp(source, 0)
