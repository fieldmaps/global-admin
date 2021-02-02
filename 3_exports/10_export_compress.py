import os
import shutil
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

cwd = Path(__file__).parent
output_path = (cwd / '10_export_compress').resolve()

output_path.mkdir(parents=True, exist_ok=True)
(output_path / 'voronoi').mkdir(parents=True, exist_ok=True)

bounds = (cwd / '00_import_boundless').resolve()

for layer in ['points', 'lines', 'polygons']:
    print(f'wld_{layer}.gpkg.zip')
    input = (cwd / f'09_export_merge/wld_{layer}.gpkg').resolve()
    output = (output_path / f'wld_{layer}.gpkg.zip').resolve()
    file = ZipFile(output, mode='w', compression=ZIP_DEFLATED)
    file.write(input, arcname=f'wld_{layer}.gpkg')
    file.close()

for layer in ['points', 'lines', 'polygons']:
    print(f'wld_{layer}.gdb')
    input = (cwd / f'09_export_merge/wld_{layer}.gpkg').resolve()
    gdb = (output_path / f'wld_{layer}.gdb').resolve()
    gdb_zip = (output_path / f'wld_{layer}.gdb').resolve()
    os.system(
        f"""docker run --rm \
        -v /Users:/Users \
        fieldmaps/gdal \
        ogr2ogr \
        -f "FileGDB" \
        {gdb} {input}"""
    )
    print(f'wld_{layer}.gdb.zip')
    shutil.make_archive(gdb_zip, 'zip', output_path, f'wld_{layer}.gdb')
    shutil.rmtree(gdb)

files_in_path = sorted(bounds.iterdir())
for in_file in files_in_path:
    if in_file.is_file() and in_file.suffix == '.gpkg':
        code = in_file.name.split('.')[0]
        print(in_file)
        output = (output_path / f'voronoi/{code}.gpkg.zip').resolve()
        file = ZipFile(output, mode='w', compression=ZIP_DEFLATED)
        file.write(in_file, arcname=f'{code}_voronoi.gpkg')
        file.close()

        gdb = (output_path / f'{code}_voronoi.gdb').resolve()
        gdb_zip = (output_path / f'voronoi/{code}.gdb').resolve()
        os.system(
            f"""docker run --rm \
            -v /Users:/Users \
            fieldmaps/gdal \
            ogr2ogr \
            -f "FileGDB" \
            {gdb} {in_file}"""
        )
        shutil.make_archive(gdb_zip, 'zip', output_path, f'{code}_voronoi.gdb')
        shutil.rmtree(gdb)
