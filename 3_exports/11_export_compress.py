from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from datetime import date

today = date.today().isoformat()

cwd = Path(__file__).parent
(cwd / '11_export_compress').mkdir(parents=True, exist_ok=True)
bounds = (cwd / '02_polygon_clip').resolve()

for layer in ['polygons', 'lines', 'points']:
    print(layer)
    input = (cwd / f'10_export_merge/wld_{layer}.gpkg').resolve()
    output = (cwd / f'11_export_compress/wld_{layer}.gpkg.zip').resolve()
    file = ZipFile(output, mode='w', compression=ZIP_DEFLATED)
    file.write(input, arcname=f'wld_{layer}_{today}.gpkg')
    file.close()

files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        print(code)
        output = (cwd /
                  f'11_export_compress/{code}.gpkg.zip').resolve()
        file = ZipFile(output, mode='w', compression=ZIP_DEFLATED)
        file.write(in_file, arcname=f'{code}_boundless_{today}.gpkg')
        file.close()
