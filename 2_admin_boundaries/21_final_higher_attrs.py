import os
import re
from pathlib import Path
from sqlite3 import connect

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


def get_attributes(level):
    result = []
    for l in range(level + 1):
        result.append(f'id_{l}')
    return ','.join(result)


def final_higher(code, level):
    input = Path(f'{cwd}/20_final_higher_dissolve/{code}.gpkg')
    output = Path(f'{cwd}/21_final_higher_attrs/{code}.gpkg')
    if os.path.isfile(input):
        print(code, 0)
        os.system(
            f"""ogr2ogr \
            -sql 'SELECT fid,geom,{get_attributes(0)} FROM "{code}_adm0"' \
            -a_srs 'EPSG:4326' \
            -nln {code}_adm0 \
            {output} {input}"""
        )
        for l in range(1, level + 1):
            print(code, l)
            layer = f'{code}_adm{l}'
            os.system(
                f"""ogr2ogr \
                -sql 'SELECT fid,geom,{get_attributes(l)} FROM "{layer}"' \
                -a_srs 'EPSG:4326' \
                -append \
                -nln {layer} \
                {output} {input}"""
            )


bounds = (cwd_path / '20_final_higher_dissolve').resolve()
files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        final_higher(code, level)
