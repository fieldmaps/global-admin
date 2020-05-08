import os
import csv
import shutil
from pathlib import Path

cwd = Path(__file__).parent
(cwd / '23_final_merge').mkdir(parents=True, exist_ok=True)

tpl = (cwd / '../0_data_inputs/boundaries/wfp_disputed.gpkg').resolve()
tpl_levels = (cwd / '../0_data_inputs/boundaries/wfp_adm0.gpkg').resolve()
output_1 = (cwd / '23_final_merge/wld.gpkg').resolve()
output_2 = (cwd / '23_final_merge/wld_levels.gpkg').resolve()
shutil.copyfile(tpl, output_1)
shutil.copyfile(tpl_levels, output_2)


with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        levels = int(row['admin_level_full'])
        input = (cwd / f'22_final_clip/{code}.gpkg').resolve()
        print(code)
        if os.path.isfile(input):
            os.system(
                f"ogr2ogr -f 'gpkg' -append -sql 'SELECT * FROM {code}_adm{levels}' -nln wld {output_1} {input}")
            for level in range(levels, 0, -1):
                os.system(
                    f"ogr2ogr -f 'gpkg' -append -sql 'SELECT * FROM {code}_adm{level}' -nln wld_adm{level} {output_2} {input}")
        else:
            code_alt = f'id_0_{code.upper()}'
            input_1 = (cwd / f'00_inputs/wld/{code_alt}.gpkg').resolve()
            os.system(
                f"ogr2ogr -f 'gpkg' -append -sql 'SELECT * FROM {code_alt}' -nln wld {output_1} {input_1}")
