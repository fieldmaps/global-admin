import os
from pathlib import Path

cwd = Path(__file__).parent
output_path = (cwd / '../../tiles/data').resolve()
output_path.mkdir(parents=True, exist_ok=True)

input = (cwd / f'09_export_merge/wld_lines.gpkg').resolve()
output = (output_path / f'land.geojsonl').resolve()
print(output)
os.system(
    f"""ogr2ogr \
    -sql "SELECT * FROM land" \
    {output} {input}"""
)
output = (output_path / 'adm0_lines.geojsonl').resolve()
print(output)
os.system(
    f"""ogr2ogr \
    -sql "SELECT * FROM adm0" \
    {output} {input}"""
)

input = (cwd / f'09_export_merge/wld_points.gpkg').resolve()
for l in range(0, 5):
    for z in range(0, 11):
        output = (output_path /
                  f'adm{l}_points_z{z}.geojsonl').resolve()
        print(output)
        extra = ''
        if l < 4:
            extra = f'AND ({z} < adm{l+1}_point OR adm{l+1}_point IS NULL)'
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM 'adm{l}' WHERE {z} >= adm{l}_point {extra}" \
            {output} {input}"""
        )

input = (cwd / f'09_export_merge/wld_lines.gpkg').resolve()
for l in range(1, 5):
    for z in range(0, 11):
        output = (output_path / f'adm{l}_lines_z{z}.geojsonl').resolve()
        print(output)
        os.system(
            f"""ogr2ogr \
            -sql "SELECT * FROM 'adm{l}' WHERE {z} >= adm{l}_line" \
            {output} {input}"""
        )
