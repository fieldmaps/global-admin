import os
import csv
import shutil
from pathlib import Path

cwd = Path(__file__).parent
(cwd / '23_final_merge').mkdir(parents=True, exist_ok=True)

tpl = (cwd / '../0_data_inputs/boundaries/wfp_adm0.gpkg').resolve()
output = (cwd / '23_final_merge/wld_levels.gpkg').resolve()
shutil.copyfile(tpl, output)


with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        levels = int(row['admin_level_full'])
        input = (cwd / f'22_final_clip/{code}.gpkg').resolve()
        print(code)
        if os.path.isfile(input):
            for level in range(1, levels + 1):
                os.system(
                    f"""ogr2ogr \
                    -sql 'SELECT * FROM {code}_adm{level}' \
                    -nln wld_adm{level} \ 
                    -append \
                    {output} {input}"""
                )
