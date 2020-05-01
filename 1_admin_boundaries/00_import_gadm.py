import csv
from pathlib import Path
import geopandas as gpd

cwd_path = Path(__file__).parent
cwd = cwd_path.resolve()
attributes = {
    '5': ['geometry', 'admin5Pcode', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '4': ['geometry', 'admin4Pcode', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '3': ['geometry', 'admin3Pcode', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '2': ['geometry', 'admin2Pcode', 'admin1Pcode', 'admin0Pcode'],
    '1': ['geometry', 'admin1Pcode', 'admin0Pcode'],
    '0': ['geometry', 'admin0Pcode'],
}
columns = ['geometry', 'GID_5', 'GID_4', 'GID_3', 'GID_2', 'GID_1', 'GID_0']
columns_new = {'GID_5': 'admin5Pcode', 'GID_4': 'admin4Pcode', 'GID_3': 'admin3Pcode',
               'GID_2': 'admin2Pcode', 'GID_1': 'admin1Pcode', 'GID_0': 'admin0Pcode'}
re_filter = r'^[Ww]ater\s?[Bb]ody|[Ll]ake$'


def add_gadm(code, level):
    input = Path(
        '{0}/originals/gadm36/GID_0_{1}.gpkg'.format(cwd, code.upper()))
    output = Path('{0}/inputs/{1}.gpkg'.format(cwd, code))
    layer = '{0}_adm{1}'.format(code, level)
    gdf = gpd.read_file(input)
    gdf = gdf[~gdf.ENGTYPE_1.str.contains(re_filter, na=False)]
    gdf = gdf[~gdf.ENGTYPE_2.str.contains(re_filter, na=False)]
    gdf = gdf[~gdf.ENGTYPE_3.str.contains(re_filter, na=False)]
    gdf = gdf[~gdf.ENGTYPE_4.str.contains(re_filter, na=False)]
    gdf = gdf[~gdf.ENGTYPE_5.str.contains(re_filter, na=False)]
    gdf.rename(columns=columns_new, inplace=True)
    gdf = gdf.filter(items=attributes[level])
    gdf.to_file(output, layer=layer, driver="GPKG")


with open((cwd_path / '../data.csv').resolve()) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        code = row['alpha_3'].lower()
        level = int(row['admin_level_full'])
        source = row['source']
        if source in ['GADM', '']:
            add_gadm(code, level)
