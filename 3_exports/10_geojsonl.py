import os
import gzip
import shutil
import pandas as pd
from pathlib import Path
from sqlite3 import connect

cwd = Path(__file__).parent
out_path = (cwd / '../../tiles/data').resolve()
out_path.mkdir(parents=True, exist_ok=True)

attrs_zoom0 = (cwd / '../0_data_inputs/attributes/wld_adm0.xlsx').resolve()
attrs_zoom = (cwd / '../0_data_inputs/attributes/wld_zoom.xlsx').resolve()
df_0 = pd.read_excel(attrs_zoom0, engine='openpyxl')
df_0 = df_0[['adm0_fid', 'adm0_point']]
df_z = pd.read_excel(attrs_zoom, engine='openpyxl')

def compress_file(output, compressed):
    with open(output, 'rb') as f_in:
        with gzip.open(compressed, 'wb', compresslevel=1) as f_out:
            shutil.copyfileobj(f_in, f_out)
            os.remove(output)

for layer in ('lines', 'polygons'):
    input = (cwd / f'09_export_merge/wld_{layer}.gpkg').resolve()
    output = (out_path / f'adm0_{layer}.geojsonl').resolve()
    compressed = (out_path / f'adm0_{layer}.geojsonl.gz').resolve()
    print(compressed)
    os.system(
        f"""ogr2ogr \
        -sql "SELECT * FROM adm0_{layer}" \
        {output} {input}"""
    )
    compress_file(output, compressed)

for layer in ('points', 'lines'):
    input = (cwd / f'09_export_merge/wld_{layer}.gpkg').resolve()
    tmp = (out_path / f'wld_{layer}.gpkg').resolve()
    print(tmp)
    shutil.copyfile(input, tmp)
    conn = connect(tmp)
    for level in range(5):
        if layer != 'lines' or level != 0:
            df = pd.read_sql_query(f'SELECT * FROM adm{level}_{layer}', conn)
            df = df.merge(df_z, on='adm0_id', how='left')
            df.to_sql(f'adm{level}_{layer}', conn, if_exists='replace', index=False)
        if layer == 'points' and level == 0:
            df = pd.read_sql_query(f'SELECT * FROM adm{level}_{layer}', conn)
            df = df.merge(df_0, on='adm0_fid', how='left')
            df.to_sql(f'adm{level}_{layer}', conn, if_exists='replace', index=False)
    conn.close()

for l in range(0, 5):
    for z in range(0, 12):
        input = (out_path / f'wld_points.gpkg').resolve()
        output = (out_path / f'adm{l}_points_z{z}.geojsonl').resolve()
        compressed = (out_path / f'adm{l}_points_z{z}.geojsonl.gz').resolve()
        print(compressed)
        extra = ''
        if l < 4:
            extra = f'AND ({z} < adm{l+1}_point OR adm{l+1}_point IS NULL)'
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM 'adm{l}_points' WHERE {z} >= adm{l}_point {extra}" \
            {output} {input}"""
        )
        compress_file(output, compressed)

for l in range(1, 5):
    for z in range(0, 12):
        input = (out_path / f'wld_lines.gpkg').resolve()
        output = (out_path / f'adm{l}_lines_z{z}.geojsonl').resolve()
        compressed = (out_path / f'adm{l}_lines_z{z}.geojsonl.gz').resolve()
        print(compressed)
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM 'adm{l}_lines' WHERE {z} = adm{l}_line" \
            {output} {input}"""
        )
        compress_file(output, compressed)

os.remove((out_path / f'wld_points.gpkg').resolve())
os.remove((out_path / f'wld_lines.gpkg').resolve())

# TESTING ONLY
# for l in range(0, 5):
#     input = (cwd / f'09_export_merge/wld_points.gpkg').resolve()
#     output = (out_path / f'adm{l}_points.geojsonl').resolve()
#     compressed = (out_path / f'adm{l}_points.geojsonl.gz').resolve()
#     print(compressed)
#     os.system(
#         f"""ogr2ogr \
#         -sql "SELECT * FROM 'adm{l}'" \
#         {output} {input}"""
#     )
#     compress_file(output, compressed)

# for l in range(1, 5):
#     input = (cwd / f'09_export_merge/wld_lines.gpkg').resolve()
#     output = (out_path / f'adm{l}_lines.geojsonl').resolve()
#     compressed = (out_path / f'adm{l}_lines.geojsonl.gz').resolve()
#     print(compressed)
#     os.system(
#         f"""ogr2ogr \
#         -sql "SELECT * FROM 'adm{l}'" \
#         {output} {input}"""
#     )
#     compress_file(output, compressed)
