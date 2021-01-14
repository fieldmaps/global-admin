import os
import gzip
import shutil
from pathlib import Path

cwd = Path(__file__).parent
out_path = (cwd / '../../tiles/data').resolve()
out_path.mkdir(parents=True, exist_ok=True)


def compress_file(output, compressed):
    with open(output, 'rb') as f_in:
        with gzip.open(compressed, 'wb', compresslevel=1) as f_out:
            shutil.copyfileobj(f_in, f_out)
            os.remove(output)


for layer, out_name in (('land', 'land'), ('adm0', 'adm0_lines')):
    input = (cwd / f'09_export_merge/wld_lines.gpkg').resolve()
    output = (out_path / f'{out_name}.geojsonl').resolve()
    compressed = (out_path / f'{out_name}.geojsonl.gz').resolve()
    print(compressed)
    os.system(
        f"""ogr2ogr \
        -sql "SELECT * FROM {layer}" \
        {output} {input}"""
    )
    compress_file(output, compressed)

for l in range(0, 5):
    for z in range(0, 11):
        input = (cwd / f'09_export_merge/wld_points.gpkg').resolve()
        output = (out_path / f'adm{l}_points_z{z}.geojsonl').resolve()
        compressed = (out_path / f'adm{l}_points_z{z}.geojsonl.gz').resolve()
        print(compressed)
        extra = ''
        if l < 4:
            extra = f'AND ({z} < adm{l+1}_point OR adm{l+1}_point IS NULL)'
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM 'adm{l}' WHERE {z} >= adm{l}_point {extra}" \
            {output} {input}"""
        )
        compress_file(output, compressed)

for l in range(1, 5):
    for z in range(0, 11):
        input = (cwd / f'09_export_merge/wld_lines.gpkg').resolve()
        output = (out_path / f'adm{l}_lines_z{z}.geojsonl').resolve()
        compressed = (out_path / f'adm{l}_lines_z{z}.geojsonl.gz').resolve()
        print(compressed)
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM 'adm{l}' WHERE {z} >= adm{l}_line" \
            {output} {input}"""
        )
        compress_file(output, compressed)
