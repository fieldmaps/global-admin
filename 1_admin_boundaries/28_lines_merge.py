import os
import csv
import shutil
from pathlib import Path

cwd = Path(__file__).parent
(cwd / '28_lines_merge').mkdir(parents=True, exist_ok=True)

tpl = (cwd / '../0_data_inputs/boundaries/wfp_adm0_lines.gpkg').resolve()
output = (cwd / '28_lines_merge/wld_lines.gpkg').resolve()
shutil.copyfile(tpl, output)


def get_attributes(level):
    result = []
    for l in range(level):
        result.append(f'id_{l}')
    return ','.join(result)


with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        levels = int(row['admin_level_full'])
        input = (cwd / f'27_lines_clip/{code}.gpkg').resolve()
        print(code)
        if os.path.isfile(input):
            for level in range(1, levels + 1):
                os.system(
                    f"""ogr2ogr \
                    -sql 'SELECT * FROM {code}_adm{level}' \
                    -nln adm{level} \
                    -select '{get_attributes(level)}' \
                    -append \
                    {output} {input}"""
                )
