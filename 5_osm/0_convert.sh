ogr2ogr \
    -where "highway='trunk' OR highway='motorway' OR highway='primary'" \
    roads-primary.gpkg planet.osm.pbf lines

ogr2ogr \
    -where "highway='secondary'" \
    roads-primary.gpkg planet.osm.pbf lines

ogr2ogr \
    -where "highway='tertiary'" \
    roads-primary.gpkg planet.osm.pbf lines

ogr2ogr \
    -where "waterway IS NOT NULL OR water IS NOT NULL OR natural IN ('water','wetland','bay')" \
    rivers.gpkg planet.osm.pbf lines

ogr2ogr \
    -where "natural IN ('water','wetland','bay')" \
    lakes.gpkg planet.osm.pbf polygons

ogr2ogr \
    -where "building IS NOT NULL" \
    buildings.gpkg planet.osm.pbf polygons
