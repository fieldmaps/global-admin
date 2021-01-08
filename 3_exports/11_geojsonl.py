import os
from pathlib import Path

cwd = Path(__file__).parent
output_path = (cwd / '../../tiles/data').resolve()
output_path.mkdir(parents=True, exist_ok=True)

for layer in ['points', 'lines']:
    input = (cwd / f'09_export_merge/wld_{layer}.gpkg').resolve()
    if layer == 'lines':
        output = (output_path / f'land.geojsonl').resolve()
        print(output)
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM land" \
            {output} {input}"""
        )
    for level in range(5):
        output = (output_path / f'adm{level}_{layer}.geojsonl').resolve()
        print(output)
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM 'adm{level}'" \
            {output} {input}"""
        )
