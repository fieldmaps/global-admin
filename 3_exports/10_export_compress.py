import shutil
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from datetime import date

today = date.today().isoformat()

cwd = Path(__file__).parent
output_path = (cwd / '10_export_compress').resolve()
shutil.rmtree(output_path, ignore_errors=True)
output_path.mkdir(parents=True, exist_ok=True)

bounds = (cwd / '00_import_boundless').resolve()

for layer in ['polygons', 'lines', 'points']:
    print(f'wld_{layer}.gpkg.zip')
    input = (cwd / f'09_export_merge/wld_{layer}.gpkg').resolve()
    output = (output_path / f'wld_{layer}.gpkg.zip').resolve()
    file = ZipFile(output, mode='w', compression=ZIP_DEFLATED)
    file.write(input, arcname=f'wld_{layer}_{today}.gpkg')
    file.close()

files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        print(f'{code}.gpkg.zip')
        output = (output_path / f'{code}.gpkg.zip').resolve()
        file = ZipFile(output, mode='w', compression=ZIP_DEFLATED)
        file.write(in_file, arcname=f'{code}_boundless_{today}.gpkg')
        file.close()
