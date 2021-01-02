import os
from pathlib import Path

cwd = Path(__file__).parent
attrs = (cwd / '../1_admin_attributes/2_merge_sources/wld.db').resolve()
attrs_adm0 = (cwd / '../0_data_inputs/attributes/wld_adm0.xlsx').resolve()

adm0_polygon_input = (
    cwd / '../0_data_inputs/boundaries/wld_adm0.gpkg').resolve()
adm0_polygon_output = (cwd / '00_import_adm0/wld.gpkg').resolve()
adm0_points_input = (
    cwd / '../0_data_inputs/boundaries/wld_adm0_points.gpkg').resolve()
adm0_points_output = (cwd / '00_import_adm0/wld_points.gpkg').resolve()

adm0_layers = [(adm0_polygon_input, adm0_polygon_output),
               (adm0_points_input, adm0_points_output)]

(cwd / '00_import_adm0').mkdir(parents=True, exist_ok=True)


for adm0_input, adm0_output in adm0_layers:
    join_sql = f"""
        SELECT *
        FROM wld_adm0 AS adm
        LEFT JOIN '{attrs}'.adm0 AS tbl1
        ON adm.id_0 = tbl1.id_0
        LEFT JOIN '{attrs_adm0}'.adm0 AS tbl2
        ON adm.id_wfp_0 = tbl2.id_wfp_0
        ORDER BY id_0, id_wfp_0 ASC
        """
    os.system(
        f"""ogr2ogr \
        -dialect INDIRECT_SQLITE \
        -sql "{join_sql}" \
        -unsetFid \
        -nln adm0 \
        {adm0_output} {adm0_input}"""
    )
