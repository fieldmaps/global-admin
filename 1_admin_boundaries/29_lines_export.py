import os
from pathlib import Path

cwd = Path(__file__).parent
(cwd / '29_lines_export').mkdir(parents=True, exist_ok=True)

input = (cwd / '28_lines_merge/wld_lines.gpkg').resolve()
output = (cwd / '29_lines_export/wld_lines.gpkg').resolve()

for level in range(5):
    if level == 0:
        os.system(
            f"""ogr2ogr \
            -sql 'SELECT * FROM adm0_disp' \
            -nln adm0_disp \
            {output} {input}"""
        )
    os.system(
        f"""ogr2ogr \
        -sql 'SELECT * FROM adm{level}' \
        -nln adm{level} \
        -append \
        {output} {input}"""
    )
