import os
import csv
from pathlib import Path

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()


def get_attributes(level):
    result = []
    for l in range(level + 1):
        result.append(f'id_{l}')
    return ','.join(result)


def final_higher(code, level):
    input = Path(f'{cwd}/20_final_higher/{code}.gpkg')
    output = Path(f'{cwd}/21_final_higher_attr/{code}.gpkg')
    if os.path.isfile(input):
        print(code)
        os.system(
            f"""ogr2ogr \
            -select 'id_0' \
            -nln {code}_adm0 \
            {output} {input}"""
        )
        for l in range(1, level + 1):
            layer = f'{code}_adm{l}'
            os.system(
                f"""ogr2ogr \
                -sql 'SELECT * FROM {layer}' \
                -select '{get_attributes(l)}' \
                -append \
                -nln {layer} \
                {output} {input}"""
            )


with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        final_higher(code, level)
