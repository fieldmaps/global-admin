import os
from pathlib import Path

cwd = Path(__file__).parent
output_path = (cwd / '11_geojsonl').resolve()
output_path.mkdir(parents=True, exist_ok=True)

for layer in ['points', 'lines', 'polygons']:
    output = (output_path / f'wld_{layer}.geojsonl').resolve()
    print(f'wld_{layer}.gpkg.zip')
    input = (cwd / f'09_export_merge/wld_{layer}.gpkg').resolve()
    os.system(
        f"""ogr2ogr \
        {output} {input}"""
    )
