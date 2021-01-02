import os
import re
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.db').resolve()
attrs_adm0 = (cwd / '../0_data_inputs/attributes/wld_adm0.xlsx').resolve()
bounds = (cwd / '../2_admin_boundaries/21_final_higher_attrs').resolve()

(cwd / '00_import_boundless').mkdir(parents=True, exist_ok=True)


def max_level_in_gpkg(in_file):
    conn = connect(in_file)
    cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
    cursor.close()
    conn.close()
    adm_list = list(filter(lambda x: re.search(r'adm\d$', x), tables))
    levels = map(lambda x: int(x[-1]), adm_list)
    return max(levels)


def add_boundless(code: str, level: int):
    input = (bounds / f'{code}.gpkg').resolve()
    output = (cwd / f'00_import_boundless/{code}.gpkg').resolve()
    for level in range(level+1):
        print(f'{code} {level}')
        if level == 0:
            join_sql = f"""
                SELECT *
                FROM {code}_adm0 AS adm
                LEFT JOIN '{attrs}'.adm0 AS tbl1
                ON adm.id_0 = tbl1.id_0
                ORDER BY id_0 ASC"""
            os.system(
                f"""ogr2ogr \
                -dialect INDIRECT_SQLITE \
                -sql "{join_sql}" \
                -nln adm{level} \
                {output} {input}"""
            )
        else:
            join_sql_list = [f"SELECT * FROM {code}_adm{level} AS adm"]
            for lvl in range(level, -1, -1):
                join_sql_list.append(
                    f"""LEFT JOIN '{attrs}'.adm{lvl} AS tbl{lvl}
                    ON adm.id_{lvl} = tbl{lvl}.id_{lvl}"""
                )
            join_sql_list.append('ORDER BY id_0 ASC')
            join_sql = ' '.join(join_sql_list)
            os.system(
                f"""ogr2ogr \
                -dialect INDIRECT_SQLITE \
                -sql "{join_sql}" \
                -unsetFid \
                -nln adm{level} \
                -append \
                {output} {input}"""
            )


files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        level = max_level_in_gpkg(in_file)
        if level > 0:
            add_boundless(code, int(level))
