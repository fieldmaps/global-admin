# https://export.hotosm.org/en/v3/
import os
from pathlib import Path

cwd = Path(__file__).parent
input_path = (cwd / '../0_data_inputs/boundaries').resolve()
output_path = (cwd / '00_import_osm').resolve()
osm_conf = (cwd / './osmconf').resolve()
output_path.mkdir(parents=True, exist_ok=True)

planet_layer = 'planet-2021-01-25.osm.pbf'

os.system(
    f"""ogr2ogr \
    -where "amenity='ferry_terminal' OR building='ferry_terminal' OR port IS NOT NULL" \
    -oo CONFIG_FILE={osm_conf}/sea_ports.ini \
    {output_path}/sea_ports.gpkg \
    {input_path}/{planet_layer} points"""
)

os.system(
    f"""ogr2ogr \
    -where "aeroway IS NOT NULL OR building = 'aerodrome' OR emergency_helipad IS NOT NULL OR emergency = 'landing_site'" \
    -oo CONFIG_FILE={osm_conf}/airports.ini \
    {output_path}/airports.gpkg \
    {input_path}/{planet_layer} points"""
)

os.system(
    f"""ogr2ogr \
    -where "amenity IN ('mobile_money_agent','bureau_de_change','bank','microfinance','atm','sacco','money_transfer','post_office')" \
    -oo CONFIG_FILE={osm_conf}/financial_services.ini \
    {output_path}/financial_services.gpkg \
    {input_path}/{planet_layer} points"""
)

os.system(
    f"""ogr2ogr \
    -where "amenity IN ('kindergarten','school','college','university') OR building IN ('kindergarten','school','college','university')" \
    -oo CONFIG_FILE={osm_conf}/education_facilities.ini \
    {output_path}/education_facilities.gpkg \
    {input_path}/{planet_layer} points"""
)

os.system(
    f"""ogr2ogr \
    -where "healthcare IS NOT NULL OR amenity IN ('doctors','dentist','clinic','hospital','pharmacy')" \
    -oo CONFIG_FILE={osm_conf}/healthsites.ini \
    {output_path}/healthsites.gpkg \
    {input_path}/{planet_layer} points"""
)

os.system(
    f"""ogr2ogr \
    -where "place IN ('isolated_dwelling','town','village','hamlet','city')" \
    -oo CONFIG_FILE={osm_conf}/populated_places.ini \
    {output_path}/populated_places.gpkg \
    {input_path}/{planet_layer} points"""
)

# os.system(
#     f"""ogr2ogr \
#     -where "amenity IS NOT NULL OR man_made IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL" \
#     -oo CONFIG_FILE={osm_conf}/points_of_interest.ini \
#     {output_path}/points_of_interest.gpkg \
#     {input_path}/{planet_layer} points"""
# )

os.system(
    f"""ogr2ogr \
    -where "railway IN ('rail','subway','station')" \
    -oo CONFIG_FILE={osm_conf}/railways.ini \
    {output_path}/railways.gpkg \
    {input_path}/{planet_layer} lines"""
)

os.system(
    f"""ogr2ogr \
    -where "highway IN ('motorway','trunk','primary','secondary','tertiary')" \
    -oo CONFIG_FILE={osm_conf}/roads.ini \
    {output_path}/roads.gpkg \
    {input_path}/{planet_layer} lines"""
)

os.system(
    f"""ogr2ogr \
    -where "waterway IS NOT NULL OR water IS NOT NULL OR natural IN ('water','wetland','bay')" \
    -oo CONFIG_FILE={osm_conf}/waterways.ini \
    {output_path}/rivers.gpkg \
    {input_path}/{planet_layer} lines"""
)

os.system(
    f"""ogr2ogr \
    -where "waterway IS NOT NULL OR water IS NOT NULL OR natural IN ('water','wetland','bay')" \
    -oo CONFIG_FILE={osm_conf}/waterways.ini \
    {output_path}/lakes.gpkg \
    {input_path}/{planet_layer} multipolygons"""
)

# os.system(
#     f"""ogr2ogr \
#     -where "building IS NOT NULL" \
#     -oo CONFIG_FILE={osm_conf}/buildings.ini \
#     {output_path}/buildings.gpkg \
#     {input_path}/{planet_layer} multipolygons"""
# )
