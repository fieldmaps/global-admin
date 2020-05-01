import os
import csv
import shutil
from pathlib import Path

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()


def merge_layers(code):
    input_1 = Path(f'{cwd}/11_outline_centroid/{code}.gpkg')
    input_2 = Path(f'{cwd}/12_outline_along/{code}.gpkg')
    input_3 = Path(f'{cwd}/07_corner_line_intersect/{code}.gpkg')
    output = Path(f'{cwd}/13_points_merge/{code}.gpkg')
    if os.path.isfile(input_1) and os.path.isfile(input_2) and os.path.isfile(input_3):
        shutil.copyfile(input_1, output)
        os.system(f"ogr2ogr -f 'gpkg' -append {output} {input_2}")
        os.system(f"ogr2ogr -f 'gpkg' -append {output} {input_3}")


with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        merge_layers(code)
