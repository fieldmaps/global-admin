import os
from pathlib import Path

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()
bounds = (cwd_path / '11_outline_centroid')

files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        print(code)
        input_2 = Path(f'{cwd}/07_corner_line_intersect/{code}.gpkg')
        output = Path(f'{cwd}/12_points_merge/{code}.gpkg')
        os.system(f"ogr2ogr -a_srs 'EPSG:4326' {output} {in_file}")
        os.system(f"ogr2ogr -a_srs 'EPSG:4326' -append {output} {input_2}")
