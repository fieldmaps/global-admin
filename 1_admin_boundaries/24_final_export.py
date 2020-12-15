import os
from pathlib import Path

cwd = Path(__file__).parent
(cwd / '24_final_export').mkdir(parents=True, exist_ok=True)

input = (cwd / '23_final_merge/wld.gpkg').resolve()
output = (cwd / '24_final_export/wld.gpkg').resolve()

db = (cwd / '../1_admin_attributes/2_merge_sources/wld.sqlite').resolve()
wfp_adm0 = (cwd / '../0_data_inputs/attributes/wfp_adm0.xlsx').resolve()


for level in range(5):
    if level == 0:
        join_sql = f"""
            SELECT *
            FROM wld_adm0 AS adm
            LEFT JOIN '{db}'.adm0 AS tbl1
            ON adm.id_0 = tbl1.id_0
            LEFT JOIN '{wfp_adm0}'.wfp_adm0 AS tbl2
            ON adm.id_0 = tbl2.id_0
            """
        os.system(
            f"""ogr2ogr \
            -dialect INDIRECT_SQLITE \
            -sql "{join_sql}" \
            -nln adm{level} \
            {output} {input}"""
        )
    else:
        join_sql_list = [f"SELECT * FROM wld_adm{level} AS adm"]
        for lvl in range(level + 1):
            join_sql_list.append(
                f"""LEFT JOIN '{db}'.adm{lvl} AS tbl{lvl}
                ON adm.id_{lvl} = tbl{lvl}.id_{lvl}"""
            )
        join_sql = ' '.join(join_sql_list)
        print(f'wld_{level}')
        os.system(
            f"""ogr2ogr \
            -dialect INDIRECT_SQLITE \
            -sql "{join_sql}" \
            -nln adm{level} \
            -append \
            {output} {input}"""
        )
